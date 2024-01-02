summarize_transcript_prompt = """
    You will be given a transcript of an audio file below delimited by <t> tags:
    ---
    <t>
    # TRANSCRIPT
    {transcript}
    # END OF TRANSCRIPT
    <t>
    ---
    Your task is to summarize the transcript.
"""
