from pythainlp.tokenize import word_tokenize

def custom_tokenizer(text):
    # Tokenize the text using pythainlp
    tokens = word_tokenize(text, engine="attacut", keep_whitespace=True)
    
    return tokens

# Test the custom tokenizer
text = "วันจันทร์ห้องสมุดเปิดไหม"
tokens = custom_tokenizer(text)
print(tokens)
