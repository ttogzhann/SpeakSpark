import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { spawn, execFileSync } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { createRequire } from 'node:module'
import { createServer } from 'vite'

const directory = dirname(fileURLToPath(import.meta.url))
const frontend = resolve(directory, '..')
const workspace = await mkdtemp(join(tmpdir(), 'speakspark-e2e-'))
const token = randomUUID()
let backend, vite, testProcess, backendOrigin
let exitCode = 1
let interrupted = false
let backendError
const delay = (milliseconds) => new Promise((resolveDelay) => setTimeout(resolveDelay, milliseconds))
function exited(child) {
  return child.exitCode !== null || child.signalCode !== null
}
async function waitExit(child, milliseconds = 5000) {
  const deadline = Date.now() + milliseconds
  while (!exited(child) && Date.now() < deadline) await delay(50)
  return exited(child)
}
function interrupt() { interrupted = true; if (testProcess && !exited(testProcess)) testProcess.kill('SIGTERM') }
process.on('SIGINT', interrupt)
process.on('SIGTERM', interrupt)
try {
  const python = process.env.E2E_PYTHON || (process.platform === 'win32'
    ? execFileSync('py', ['-3', '-c', 'import sys;print(sys.executable)'], { encoding: 'utf8' }).trim()
    : 'python3')
  backend = spawn(python, [join(directory, 'backend_server.py'), resolve(frontend, '../backend'), workspace, token], { stdio: 'inherit', windowsHide: true })
  backend.on('error', (error) => { backendError = error })
  let ready = false
  const deadline = Date.now() + 30000
  while (Date.now() < deadline && !exited(backend)) {
    if (interrupted || backendError) throw backendError || new Error('E2E run interrupted')
    try {
      const { port } = JSON.parse(await readFile(join(workspace, 'server.json'), 'utf8'))
      backendOrigin = `http://127.0.0.1:${port}`
      const response = await fetch(`${backendOrigin}/__e2e__/${token}`)
      if (response.ok && (await response.json()).token === token) { ready = true; break }
    } catch { /* owned server is still starting */ }
    await delay(100)
  }
  if (!ready) throw new Error('Isolated backend failed to become ready')
  if (interrupted) throw new Error('E2E run interrupted')
  vite = await createServer({ root: frontend, configFile: join(frontend, 'vite.config.ts'), server: { host: '127.0.0.1', port: 0, proxy: { '/api': { target: backendOrigin, rewrite: (path) => path.replace(/^\/api/, '') } } } })
  await vite.listen()
  const address = vite.httpServer.address()
  const require = createRequire(import.meta.url)
  testProcess = spawn(process.execPath, [require.resolve('@playwright/test/cli'), 'test', '--config', join(directory, 'playwright.config.ts'), ...process.argv.slice(2)], {
    cwd: frontend, stdio: 'inherit', windowsHide: true,
    env: { ...process.env, E2E_BASE_URL: `http://127.0.0.1:${address.port}` },
  })
  exitCode = await new Promise((resolveExit, reject) => { testProcess.once('error', reject); testProcess.once('exit', (code) => resolveExit(code ?? 1)) })
} catch (error) {
  console.error(error)
} finally {
  if (testProcess && !exited(testProcess)) { testProcess.kill('SIGTERM'); await waitExit(testProcess) }
  if (vite) await vite.close()
  if (backend && !exited(backend)) {
    try { await fetch(`${backendOrigin}/__e2e__/${token}/shutdown`, { method: 'POST', signal: AbortSignal.timeout(2000) }) } catch { /* direct child fallback below */ }
    if (!await waitExit(backend)) { backend.kill('SIGTERM'); await waitExit(backend) }
    if (!exited(backend)) { backend.kill('SIGKILL'); await waitExit(backend) }
  }
  await rm(workspace, { recursive: true, force: true })
  process.exitCode = exitCode
}
