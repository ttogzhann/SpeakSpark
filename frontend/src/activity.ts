export interface Activity {
  id: string
  title: string
  level: 'A1' | 'A2' | 'B1' | 'B2'
  topic: 'Daily Life' | 'Travel' | 'Food' | 'Education' | 'Work' | 'Hobbies' | 'Technology' | 'Relationships'
  type: 'Conversation Card' | 'Role-play' | 'Speaking Challenge'
  prompt: string
  is_builtin: boolean
  follow_up_questions?: string[]
  useful_phrases?: string[]
  roles?: { participant: string; objective: string }[]
  instructions?: string[]
}
