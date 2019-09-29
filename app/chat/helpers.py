def get_sorted_chats(chats):
    return sorted(
        [chat for chat in chats],
        key=lambda c: max(m.created_at for m in c.messages) if c.messages.count() else c.created_at,
        reverse=True
    )