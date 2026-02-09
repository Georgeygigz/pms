# Maintainance request transitions
MR_TRANSITIONS = {
     "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"closed"},
    "closed": set(),
}

# Work Order transitions
WO_TRANSITIONS = {
    "pending": {"accepted", "rejected"},
    "accepted": {"completed"},
    "completed": set(),
    "rejected": set(),
}