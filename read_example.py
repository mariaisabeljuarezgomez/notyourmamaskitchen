content = open('indexexample.html', encoding='utf-8').read()

# Extract DESSERTS section
idx = content.find('Peach Cobbler')
chunk = content[idx-300:idx+600]
with open('desserts_chunk.txt', 'w', encoding='utf-8') as f:
    f.write(chunk)
print(chunk)
