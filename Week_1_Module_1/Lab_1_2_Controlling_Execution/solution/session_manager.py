import json
import os
import sys
import uuid

import anthropic


# Allow Windows Command Prompt to print Unicode characters.
sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------
# SESSION STORAGE LOCATION
# ---------------------------------------------------------

# Store sessions in a "sessions" folder located beside this file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")


# ---------------------------------------------------------
# ANTHROPIC CLIENT
# ---------------------------------------------------------

# The client automatically reads ANTHROPIC_API_KEY
# from the Windows environment variable.
client = anthropic.Anthropic()


# ---------------------------------------------------------
# CREATE A NEW SESSION
# ---------------------------------------------------------

def new_session():
    """
    Creates and returns a new investigation session.
    """

    return {
        "id": uuid.uuid4().hex[:6],
        "parent_id": None,
        "messages": [],
        "summary": ""
    }


# ---------------------------------------------------------
# ADD MESSAGES
# ---------------------------------------------------------

def add_user(session, text):
    """
    Adds a user message to the session.
    """

    session["messages"].append(
        {
            "role": "user",
            "content": text
        }
    )


def add_assistant(session, text):
    """
    Adds an assistant message to the session.
    """

    session["messages"].append(
        {
            "role": "assistant",
            "content": text
        }
    )


# ---------------------------------------------------------
# SAVE SESSION
# ---------------------------------------------------------

def save_session(session):
    """
    Saves a session as a JSON file.
    Returns the full file path.
    """

    os.makedirs(SESSIONS_DIR, exist_ok=True)

    file_path = os.path.join(
        SESSIONS_DIR,
        f"{session['id']}.json"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            session,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"[SAVED] Session {session['id']} "
        f"with {len(session['messages'])} messages."
    )

    print(f"[PATH] {file_path}")

    return file_path


# ---------------------------------------------------------
# RESUME SESSION
# ---------------------------------------------------------

def resume_session(session_id):
    """
    Loads a previously saved investigation session.
    """

    file_path = os.path.join(
        SESSIONS_DIR,
        f"{session_id}.json"
    )

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Session '{session_id}' was not found at "
            f"'{file_path}'."
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        session = json.load(file)

    print(
        f"[RESUMED] Session {session['id']} "
        f"with {len(session['messages'])} messages."
    )

    return session


# ---------------------------------------------------------
# FORK SESSION
# ---------------------------------------------------------

def fork_session(parent):
    """
    Creates a separate child session.

    The child receives a copy of the parent's messages.
    The child does not share the same messages list.
    """

    child = new_session()

    child["parent_id"] = parent["id"]

    # Important:
    # Use list(...) to create a separate list.
    child["messages"] = list(parent["messages"])

    child["summary"] = parent["summary"]

    print(
        f"[FORKED] Parent session {parent['id']} "
        f"created child session {child['id']}."
    )

    return child


# ---------------------------------------------------------
# SUMMARIZE SESSION
# ---------------------------------------------------------

def summarize_session(session, keep_recent=2):
    """
    Summarizes older messages using Claude.

    Keeps the most recent messages unchanged and places
    the structured summary in session["summary"].
    """

    messages = session["messages"]

    if keep_recent < 0:
        raise ValueError(
            "keep_recent cannot be a negative number."
        )

    if len(messages) <= keep_recent:
        print(
            "[SUMMARY SKIPPED] There are not enough older "
            "messages to summarize."
        )

        return session

    if keep_recent == 0:
        older_messages = messages
        recent_messages = []
    else:
        older_messages = messages[:-keep_recent]
        recent_messages = messages[-keep_recent:]

    transcript_parts = []

    for message in older_messages:
        role = message["role"].upper()
        content = message["content"]

        transcript_parts.append(
            f"{role}:\n{content}"
        )

    transcript = "\n\n".join(transcript_parts)

    print(
        f"[SUMMARIZING] Compressing "
        f"{len(older_messages)} older messages."
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=(
            "You summarize Security Operations Center investigations. "
            "Return exactly three sections with these headings:\n"
            "DECISIONS:\n"
            "FACTS:\n"
            "OPEN:\n\n"
            "DECISIONS must contain actions already decided or completed. "
            "FACTS must contain confirmed investigation evidence. "
            "OPEN must contain unresolved questions and next steps. "
            "Never drop concrete values including alert IDs, IP addresses, "
            "hostnames, usernames, hashes, timestamps, ticket numbers, "
            "legal-hold IDs, case IDs, and file names. "
            "Do not invent information."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    "Summarize this investigation transcript:\n\n"
                    + transcript
                )
            }
        ]
    )

    summary_parts = []

    for block in response.content:
        if block.type == "text":
            summary_parts.append(block.text)

    session["summary"] = "\n".join(
        summary_parts
    ).strip()

    # Only keep the most recent messages.
    session["messages"] = recent_messages

    print(
        f"[SUMMARIZED] Session now contains "
        f"{len(session['messages'])} recent messages."
    )

    return session


# ---------------------------------------------------------
# PRINT SESSION DETAILS
# ---------------------------------------------------------

def print_session(session, title):
    """
    Prints a readable view of a session.
    """

    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print(f"Session ID: {session['id']}")
    print(f"Parent ID:  {session['parent_id']}")
    print(f"Messages:   {len(session['messages'])}")

    if session["summary"]:
        print("\nSUMMARY:")
        print(session["summary"])

    print("\nMESSAGES:")

    if not session["messages"]:
        print("No messages available.")

    for number, message in enumerate(
        session["messages"],
        start=1
    ):
        print(
            f"\n{number}. "
            f"{message['role'].upper()}"
        )

        print(message["content"])


# ---------------------------------------------------------
# MAIN DEMONSTRATION
# ---------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("LAB 1.2 EXERCISE 3: SESSION MANAGEMENT")
    print("=" * 70)

    # =====================================================
    # DEMO 1: SAVE AND RESUME
    # =====================================================

    print("\n" + "=" * 70)
    print("DEMO 1: SAVE AND RESUME")
    print("=" * 70)

    day_one_session = new_session()

    print(
        f"\nCreated new session: "
        f"{day_one_session['id']}"
    )

    add_user(
        day_one_session,
        (
            "Day 1, 02:47 EST. Sarah Chen, Tier-1 night shift, "
            "opened alert NG-2027-1142. "
            "Asset research-analyst-laptop-04 transferred "
            "8.3 GB to external IP 203.0.113.47."
        )
    )

    add_assistant(
        day_one_session,
        (
            "SIEM query confirmed outbound traffic to "
            "203.0.113.47 between 02:40 and 02:55 EST. "
            "No active VPN session was found."
        )
    )

    add_user(
        day_one_session,
        (
            "Badge records show Maya Iyer left the office "
            "at 18:22 EST. Leading hypotheses are account "
            "compromise, external APT activity, or insider threat."
        )
    )

    add_assistant(
        day_one_session,
        (
            "Decision: preserve endpoint evidence and quarantine "
            "research-analyst-laptop-04. Do not quarantine "
            "trading-prod-01 because it is a protected asset."
        )
    )

    saved_id = day_one_session["id"]

    save_session(day_one_session)

    print(
        "\nShift ending. Removing the in-memory session "
        "to simulate a shift change."
    )

    del day_one_session

    print(
        "\nDay 2, 08:00 EST. Mike Torres, Tier-2 lead, "
        "resumes the investigation."
    )

    resumed_session = resume_session(saved_id)

    print_session(
        resumed_session,
        "RESUMED INVESTIGATION"
    )

    # =====================================================
    # DEMO 2: FORK
    # =====================================================

    print("\n" + "=" * 70)
    print("DEMO 2: FORK INTO TWO HYPOTHESES")
    print("=" * 70)

    insider_branch = fork_session(
        resumed_session
    )

    external_apt_branch = fork_session(
        resumed_session
    )

    # Branch A: insider-threat investigation.
    add_user(
        insider_branch,
        (
            "Branch A hypothesis: insider threat. "
            "Check HR records, recent performance actions, "
            "departure notices, and authorized research transfers."
        )
    )

    add_assistant(
        insider_branch,
        (
            "HR review identified no departure notice. "
            "Maya Iyer remains actively employed. "
            "Open question: determine whether another individual "
            "used the laptop after the 18:22 EST badge departure."
        )
    )

    # Branch B: external-APT investigation.
    add_user(
        external_apt_branch,
        (
            "Branch B hypothesis: external APT compromise. "
            "Acquire memory image, process tree, persistence data, "
            "and network indicators."
        )
    )

    add_assistant(
        external_apt_branch,
        (
            "Memory acquisition requested. "
            "Review process tree for unsigned executables, "
            "credential theft, persistence mechanisms, and "
            "connections to IP 203.0.113.47."
        )
    )

    save_session(insider_branch)
    save_session(external_apt_branch)

    print_session(
        insider_branch,
        "BRANCH A: INSIDER-THREAT HYPOTHESIS"
    )

    print_session(
        external_apt_branch,
        "BRANCH B: EXTERNAL-APT HYPOTHESIS"
    )

    print("\nFORK VERIFICATION:")

    print(
        f"Parent session ID: "
        f"{resumed_session['id']}"
    )

    print(
        f"Branch A parent ID: "
        f"{insider_branch['parent_id']}"
    )

    print(
        f"Branch B parent ID: "
        f"{external_apt_branch['parent_id']}"
    )

    print(
        f"Branch A session ID: "
        f"{insider_branch['id']}"
    )

    print(
        f"Branch B session ID: "
        f"{external_apt_branch['id']}"
    )

    print(
        "Message lists are separate objects: "
        f"{insider_branch['messages'] is not external_apt_branch['messages']}"
    )

    # =====================================================
    # DEMO 3: SUMMARIZE
    # =====================================================

    print("\n" + "=" * 70)
    print("DEMO 3: STRUCTURED SUMMARIZATION")
    print("=" * 70)

    long_session = new_session()

    add_user(
        long_session,
        (
            "Alert NG-2027-1142 opened for "
            "research-analyst-laptop-04."
        )
    )

    add_assistant(
        long_session,
        (
            "Confirmed 8.3 GB outbound transfer to "
            "203.0.113.47 at 02:47 EST."
        )
    )

    add_user(
        long_session,
        (
            "SIEM query found connections between "
            "02:40 and 02:55 EST."
        )
    )

    add_assistant(
        long_session,
        (
            "Decision: quarantine "
            "research-analyst-laptop-04 and preserve evidence."
        )
    )

    add_user(
        long_session,
        (
            "Memory image collected with SHA-256 hash "
            "44d88612fea8a8f36de82e1278abb02f."
        )
    )

    add_assistant(
        long_session,
        (
            "Legal preservation requested under "
            "legal-hold ID L-2027-44."
        )
    )

    add_user(
        long_session,
        (
            "Forensic case number is CASE-NG-2027-1142. "
            "Maya Iyer's badge departure time was 18:22 EST."
        )
    )

    add_assistant(
        long_session,
        (
            "Open question: Was the transfer caused by account "
            "compromise, insider activity, or external APT access?"
        )
    )

    add_user(
        long_session,
        (
            "Recent message: security team requested process-tree "
            "analysis and persistence review."
        )
    )

    add_assistant(
        long_session,
        (
            "Recent message: process-tree analysis is pending. "
            "Do not release the endpoint from quarantine."
        )
    )

    print(
        f"\nMessages before summarization: "
        f"{len(long_session['messages'])}"
    )

    summarize_session(
        long_session,
        keep_recent=2
    )

    print_session(
        long_session,
        "SUMMARIZED INVESTIGATION"
    )

    save_session(long_session)

    print("\nCONCRETE-VALUE VERIFICATION:")

    values_to_check = [
        "NG-2027-1142",
        "203.0.113.47",
        "research-analyst-laptop-04",
        "44d88612fea8a8f36de82e1278abb02f",
        "L-2027-44",
        "CASE-NG-2027-1142"
    ]

    combined_text = (
        long_session["summary"]
        + "\n"
        + json.dumps(
            long_session["messages"],
            ensure_ascii=False
        )
    )

    for value in values_to_check:
        if value in combined_text:
            print(f"[PRESERVED] {value}")
        else:
            print(f"[MISSING]   {value}")

    print("\n" + "=" * 70)
    print("SESSION MANAGEMENT DEMONSTRATION COMPLETED")
    print("=" * 70)