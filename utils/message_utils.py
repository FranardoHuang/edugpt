from discord import Message

async def send_split_message(self, response: str, message: Message,send=True):
    char_limit = 1900
    msg_list = []
    # print(len(response))
    # print(response)
    if len(response) > char_limit and "```" not in response:
        is_code_block = False
        parts = response.split("```")

        for i in range(len(parts)):
            if is_code_block:
                code_block_chunks = []
                for i in range(len(parts)):
                    start = 0
                    while start < len(parts[i]):
                        end = start + char_limit
                        if end >= len(parts[i]):
                            code_block_chunks.append(parts[i][start:])
                            break

                        split_pos = parts[i].rfind('\n\n', start, end)
                        if split_pos == -1:
                            split_pos = parts[i].rfind('\n', start, end)

                        if split_pos == -1:
                            split_pos = end

                        code_block_chunks.append(parts[i][start:split_pos])
                        start = split_pos
                for chunk in code_block_chunks:
                    if send:
                        if self.is_replying_all:
                            msg=await message.channel.send(f"```{chunk}```")
                        else:
                            msg=await message.followup.send(f"```{chunk}```")
                    else:
                        msg_list.append(f"```{chunk}```")
                is_code_block = False
            else:
                non_code_chunks = []
                for i in range(len(parts)):
                    start = 0
                    while start < len(parts[i]):
                        end = start + char_limit
                        if end >= len(parts[i]):
                            non_code_chunks.append(parts[i][start:])
                            break

                        split_pos = parts[i].rfind('\n\n', start, end)
                        if split_pos == -1:
                            split_pos = parts[i].rfind('\n', start, end)

                        if split_pos == -1:
                            split_pos = end

                        non_code_chunks.append(parts[i][start:split_pos])
                        start = split_pos
                for chunk in non_code_chunks:
                    if send:
                        if self.is_replying_all:
                            msg=await message.channel.send(chunk)
                        else:
                            msg=await message.followup.send(chunk)
                    else:
                        msg_list.append(chunk)
                is_code_block = True
    else:
        if send:
            if self.is_replying_all:
                msg=await message.channel.send(response)
            else:
                msg=await message.followup.send(response)
        else:
            msg_list.append(response)
    return msg if send else msg_list

async def send_split_message_user(user,response,send=True):
    char_limit = 1900
    msg_list = []
    if len(response) > char_limit and "```" not in response:
        is_code_block = False
        parts = response.split("```")
        for i in range(len(parts)):
            if is_code_block:
                code_block_chunks = []
                for i in range(len(parts)):
                    start = 0
                    while start < len(parts[i]):
                        end = start + char_limit
                        if end >= len(parts[i]):
                            code_block_chunks.append(parts[i][start:])
                            break

                        split_pos = parts[i].rfind('\n\n', start, end)
                        if split_pos == -1:
                            split_pos = parts[i].rfind('\n', start, end)

                        if split_pos == -1:
                            split_pos = end

                        code_block_chunks.append(parts[i][start:split_pos])
                        start = split_pos
                for chunk in code_block_chunks:
                    if send:
                        msg = await user.send(f"```{chunk}```")
                    else:
                        msg_list.append(f"```{chunk}```")
                is_code_block = False
            else:
                non_code_chunks = []
                for i in range(len(parts)):
                    start = 0
                    while start < len(parts[i]):
                        end = start + char_limit
                        if end >= len(parts[i]):
                            non_code_chunks.append(parts[i][start:])
                            break

                        split_pos = parts[i].rfind('\n\n', start, end)
                        if split_pos == -1:
                            split_pos = parts[i].rfind('\n', start, end)

                        if split_pos == -1:
                            split_pos = end

                        non_code_chunks.append(parts[i][start:split_pos])
                        start = split_pos
                for chunk in non_code_chunks:
                    if send:
                        msg = await user.send(chunk)
                    else:
                        msg_list.append(chunk)
                is_code_block = True
    else:
        if send:
            msg = await user.send(response)
        else:
            msg_list.append(response)
    return msg if send else msg_list
