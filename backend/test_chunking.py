from app.utils.text_splitter import split_text_into_chunks

sample_text = "abcd"* 1000  # A long string of 'abc's

chunks = split_text_into_chunks(sample_text, chunk_size=700, overlap=100)

print(f"[DEBUG] Number of chunks created: {len(chunks)}")
for i, chunk in enumerate(chunks[:3]):
    print(chunk)  # Print the first 50 characters of each chunk