from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BuiltInActivity
from app.schemas.activity import Activity

BUILT_IN_ACTIVITY_DATA: tuple[tuple[str, dict[str, object]], ...] = (
    (
        "builtin-card-daily-life-01",
        {
            "title": "A Good Morning",
            "level": "A1",
            "topic": "Daily Life",
            "type": "Conversation Card",
            "prompt": "What do you usually do in the morning?",
            "follow_up_questions": ["What time do you get up?", "What do you eat for breakfast?"],
        },
    ),
    (
        "builtin-card-travel-01",
        {
            "title": "A Memorable Journey",
            "level": "A2",
            "topic": "Travel",
            "type": "Conversation Card",
            "prompt": "What is a memorable journey you have taken?",
            "follow_up_questions": ["Where did you go?", "What did you enjoy most?"],
        },
    ),
    (
        "builtin-card-food-01",
        {
            "title": "Food You Love",
            "level": "A1",
            "topic": "Food",
            "type": "Conversation Card",
            "prompt": "What food do you like to eat?",
            "follow_up_questions": ["Who cooks it?", "When do you eat it?"],
        },
    ),
    (
        "builtin-card-education-01",
        {
            "title": "A Useful Thing You Learned",
            "level": "B1",
            "topic": "Education",
            "type": "Conversation Card",
            "prompt": "What is something useful you learned at school or in a course?",
        },
    ),
    (
        "builtin-card-work-01",
        {
            "title": "A Great Working Day",
            "level": "B2",
            "topic": "Work",
            "type": "Conversation Card",
            "prompt": "What makes a working day feel productive and satisfying?",
            "follow_up_questions": ["How do you stay focused?", "What helps a team work well?"],
        },
    ),
    (
        "builtin-card-hobbies-01",
        {
            "title": "A Hobby to Try",
            "level": "A2",
            "topic": "Hobbies",
            "type": "Conversation Card",
            "prompt": "What hobby would you like to try, and why?",
        },
    ),
    (
        "builtin-card-technology-01",
        {
            "title": "Technology Every Day",
            "level": "B1",
            "topic": "Technology",
            "type": "Conversation Card",
            "prompt": "Which piece of technology do you use most, and how does it help you?",
        },
    ),
    (
        "builtin-card-relationships-01",
        {
            "title": "Being a Good Friend",
            "level": "A2",
            "topic": "Relationships",
            "type": "Conversation Card",
            "prompt": "What does a good friend do?",
            "follow_up_questions": ["How do you spend time with friends?"],
        },
    ),
    (
        "builtin-card-daily-life-02",
        {
            "title": "A Calm Evening",
            "level": "B1",
            "topic": "Daily Life",
            "type": "Conversation Card",
            "prompt": "How do you like to spend a relaxing evening?",
        },
    ),
    (
        "builtin-card-travel-02",
        {
            "title": "City or Countryside",
            "level": "B2",
            "topic": "Travel",
            "type": "Conversation Card",
            "prompt": "Would you rather explore a busy city or a quiet countryside? Explain your choice.",
        },
    ),
    (
        "builtin-card-food-02",
        {
            "title": "Cooking at Home",
            "level": "B1",
            "topic": "Food",
            "type": "Conversation Card",
            "prompt": "What makes a home-cooked meal special?",
        },
    ),
    (
        "builtin-card-education-02",
        {
            "title": "Learning Something New",
            "level": "A2",
            "topic": "Education",
            "type": "Conversation Card",
            "prompt": "What would you like to learn next?",
        },
    ),
    (
        "builtin-roleplay-daily-life-01",
        {
            "title": "Planning a Weekend",
            "level": "A2",
            "topic": "Daily Life",
            "type": "Role-play",
            "prompt": "Two friends are planning what to do together this weekend.",
            "roles": [
                {"participant": "Friend A", "objective": "Suggest an activity and a time."},
                {"participant": "Friend B", "objective": "Ask questions and agree on a plan."},
            ],
            "useful_phrases": ["How about...?", "That sounds great."],
        },
    ),
    (
        "builtin-roleplay-travel-01",
        {
            "title": "Checking In at a Hotel",
            "level": "A1",
            "topic": "Travel",
            "type": "Role-play",
            "prompt": "A traveler arrives at a hotel and wants to check in.",
            "roles": [
                {"participant": "Guest", "objective": "Give your name and ask about breakfast."},
                {"participant": "Receptionist", "objective": "Find the booking and explain check-in."},
            ],
            "useful_phrases": ["I have a reservation.", "What time is breakfast?"],
        },
    ),
    (
        "builtin-roleplay-food-01",
        {
            "title": "Ordering Lunch",
            "level": "A1",
            "topic": "Food",
            "type": "Role-play",
            "prompt": "A customer orders lunch at a small café.",
            "roles": [
                {"participant": "Customer", "objective": "Order a meal and a drink."},
                {"participant": "Server", "objective": "Describe two menu choices and take the order."},
            ],
        },
    ),
    (
        "builtin-roleplay-education-01",
        {
            "title": "Asking About a Course",
            "level": "B1",
            "topic": "Education",
            "type": "Role-play",
            "prompt": "A prospective student asks a course adviser about joining a class.",
            "roles": [
                {"participant": "Student", "objective": "Ask about the schedule and course materials."},
                {"participant": "Adviser", "objective": "Explain the class and recommend next steps."},
            ],
        },
    ),
    (
        "builtin-roleplay-work-01",
        {
            "title": "A First Day at Work",
            "level": "B1",
            "topic": "Work",
            "type": "Role-play",
            "prompt": "A new colleague meets a teammate during their first day at work.",
            "roles": [
                {"participant": "New colleague", "objective": "Introduce yourself and ask about the team."},
                {"participant": "Teammate", "objective": "Welcome them and explain a daily routine."},
            ],
        },
    ),
    (
        "builtin-roleplay-hobbies-01",
        {
            "title": "Joining a Sports Club",
            "level": "A2",
            "topic": "Hobbies",
            "type": "Role-play",
            "prompt": "Someone visits a local sports club to find out how to join.",
            "roles": [
                {"participant": "Visitor", "objective": "Ask about activities, times, and costs."},
                {"participant": "Club member", "objective": "Describe the club and help them choose."},
            ],
        },
    ),
    (
        "builtin-roleplay-technology-01",
        {
            "title": "Getting Help with a Phone",
            "level": "A2",
            "topic": "Technology",
            "type": "Role-play",
            "prompt": "A customer visits a shop because their phone will not connect to Wi-Fi.",
            "roles": [
                {"participant": "Customer", "objective": "Explain the problem and ask for help."},
                {"participant": "Shop assistant", "objective": "Ask questions and suggest a solution."},
            ],
            "useful_phrases": ["It stopped working yesterday.", "Could you show me how?"],
        },
    ),
    (
        "builtin-roleplay-relationships-01",
        {
            "title": "Welcoming a New Neighbor",
            "level": "A1",
            "topic": "Relationships",
            "type": "Role-play",
            "prompt": "A neighbor meets someone who has just moved into the building.",
            "roles": [
                {"participant": "New neighbor", "objective": "Introduce yourself and ask about the area."},
                {"participant": "Neighbor", "objective": "Welcome them and recommend a nearby place."},
            ],
        },
    ),
    (
        "builtin-roleplay-daily-life-02",
        {
            "title": "Returning a Library Book",
            "level": "B2",
            "topic": "Daily Life",
            "type": "Role-play",
            "prompt": "A library visitor discovers a book is overdue and asks for help.",
            "roles": [
                {"participant": "Visitor", "objective": "Explain the situation and ask about the fee."},
                {"participant": "Librarian", "objective": "Explain the policy and suggest a solution."},
            ],
        },
    ),
    (
        "builtin-roleplay-travel-02",
        {
            "title": "Finding the Train Platform",
            "level": "A2",
            "topic": "Travel",
            "type": "Role-play",
            "prompt": "A traveler asks station staff for help finding the right train platform.",
            "roles": [
                {"participant": "Traveler", "objective": "Explain where you need to go and ask for directions."},
                {"participant": "Station staff", "objective": "Give clear directions and confirm the train time."},
            ],
        },
    ),
    (
        "builtin-roleplay-food-02",
        {
            "title": "Choosing a Restaurant",
            "level": "B2",
            "topic": "Food",
            "type": "Role-play",
            "prompt": "Two friends choose a restaurant for a special dinner.",
            "roles": [
                {"participant": "Friend A", "objective": "Suggest a restaurant and explain your preference."},
                {"participant": "Friend B", "objective": "Compare the options and reach a decision."},
            ],
        },
    ),
    (
        "builtin-roleplay-education-02",
        {
            "title": "Study Group Discussion",
            "level": "B2",
            "topic": "Education",
            "type": "Role-play",
            "prompt": "Two classmates organize a study group before an important exam.",
            "roles": [
                {"participant": "Classmate A", "objective": "Suggest a study plan and divide topics."},
                {"participant": "Classmate B", "objective": "Raise a concern and negotiate a schedule."},
            ],
        },
    ),
    (
        "builtin-challenge-daily-life-01",
        {
            "title": "The Perfect Daily Routine",
            "level": "A1",
            "topic": "Daily Life",
            "type": "Speaking Challenge",
            "prompt": "Create and describe a simple daily routine from morning to evening.",
            "instructions": ["Use at least five time words such as first, then, and finally."],
        },
    ),
    (
        "builtin-challenge-travel-01",
        {
            "title": "Pack for an Adventure",
            "level": "A2",
            "topic": "Travel",
            "type": "Speaking Challenge",
            "prompt": "Imagine a three-day trip to a place you have never visited and explain what you will pack.",
            "instructions": ["Choose five items and explain why each one is useful."],
        },
    ),
    (
        "builtin-challenge-food-01",
        {
            "title": "Invent a Sandwich",
            "level": "A1",
            "topic": "Food",
            "type": "Speaking Challenge",
            "prompt": "Invent a new sandwich and describe what is inside it.",
            "instructions": ["Give your sandwich a memorable name."],
        },
    ),
    (
        "builtin-challenge-education-01",
        {
            "title": "Teach a Mini Lesson",
            "level": "B1",
            "topic": "Education",
            "type": "Speaking Challenge",
            "prompt": "Teach your partner how to do something you know well.",
            "instructions": ["Organize your explanation into three clear steps."],
        },
    ),
    (
        "builtin-challenge-work-01",
        {
            "title": "Pitch a New Idea",
            "level": "B2",
            "topic": "Work",
            "type": "Speaking Challenge",
            "prompt": "Pitch an imaginative improvement that could make a workplace better.",
            "instructions": ["Describe the problem, your idea, and its likely benefit."],
        },
    ),
    (
        "builtin-challenge-hobbies-01",
        {
            "title": "Design a New Hobby",
            "level": "A2",
            "topic": "Hobbies",
            "type": "Speaking Challenge",
            "prompt": "Invent a fun new hobby and explain how someone could get started.",
        },
    ),
    (
        "builtin-challenge-technology-01",
        {
            "title": "A Helpful Invention",
            "level": "B1",
            "topic": "Technology",
            "type": "Speaking Challenge",
            "prompt": "Imagine a simple invention that would solve a problem in everyday life.",
            "instructions": ["Describe the problem, how the invention works, and who would use it."],
        },
    ),
    (
        "builtin-challenge-relationships-01",
        {
            "title": "Plan a Welcome Party",
            "level": "A2",
            "topic": "Relationships",
            "type": "Speaking Challenge",
            "prompt": "Plan a small welcome party for a new person in your community.",
            "instructions": ["Choose a place, two activities, and something to eat."],
        },
    ),
    (
        "builtin-challenge-daily-life-02",
        {
            "title": "A Day Without Screens",
            "level": "B1",
            "topic": "Daily Life",
            "type": "Speaking Challenge",
            "prompt": "Imagine spending one day without a phone, computer, or television and describe your plan.",
        },
    ),
    (
        "builtin-challenge-travel-02",
        {
            "title": "Create a City Walking Tour",
            "level": "B2",
            "topic": "Travel",
            "type": "Speaking Challenge",
            "prompt": "Design a walking tour for a visitor and present its route and highlights.",
            "instructions": ["Include three stops and explain the order you chose."],
        },
    ),
    (
        "builtin-challenge-food-02",
        {
            "title": "Describe a Food Festival",
            "level": "B1",
            "topic": "Food",
            "type": "Speaking Challenge",
            "prompt": "Create a food festival and persuade people to visit it.",
            "instructions": ["Describe the food, the atmosphere, and one special event."],
        },
    ),
    (
        "builtin-challenge-education-02",
        {
            "title": "The Ideal Classroom",
            "level": "A2",
            "topic": "Education",
            "type": "Speaking Challenge",
            "prompt": "Design an ideal classroom and explain what students can do there.",
        },
    ),
)


def seed_builtin_activities(session: Session) -> None:
    existing_ids = set(session.scalars(select(BuiltInActivity.id)))
    for activity_id, activity_data in BUILT_IN_ACTIVITY_DATA:
        if activity_id in existing_ids:
            continue
        validated_activity = Activity.model_validate(activity_data)
        session.add(
            BuiltInActivity(
                id=activity_id,
                **validated_activity.model_dump(mode="json"),
                is_builtin=True,
            )
        )
    session.commit()
