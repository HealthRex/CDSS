from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import pandas as pd
import torch
torch.cuda.empty_cache()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")



# Load Stella model and tokenizer
model_name = "dunzhang/stella_en_1.5B_v5"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)

# read the file and retrurn chuck of notes
def Read_chunk(file_path,chunk_size=10):
    data= pd.read_csv(file_path)
    data = data.dropna()
    data = data.reset_index(drop=True)
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i + chunk_size]
        chunks.append(chunk)
    return chunks
    
if __name__ == "__main__":
    file_path = "~/PEDs/data/Val_set.csv"
    import pdb
    chunks = Read_chunk(file_path, chunk_size=10)
    DF=pd.DataFrame()
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}:")
        
        text = chunk['deid_note_text'].tolist()
        inputs = tokenizer(text, return_tensors="pt",max_length=512, padding=True, truncation=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
            attentions = outputs.attentions  # This is a list of attention matrices for each layer
      
        attention_weights = attentions[-1].mean(dim=1)  # Average over heads
        attention_weights = F.softmax(attention_weights, dim=-1)  # Apply softmax
        weighted_embedding = torch.matmul(attention_weights, outputs.last_hidden_state)
        sentence_embedding = weighted_embedding.mean(dim=1).cpu().numpy()
       
        chunk['sentence_qmbedding'] = sentence_embedding.tolist()
        if len(DF) == 0:
            DF = chunk
        else:
            DF = pd.concat([DF, chunk])
        DF.to_csv("~/PEDs/data/Val_set_with_embeddings.csv", index=False)
        print(f"Chunk {i+1} processed and saved.")
    # Save the final DataFrame to a CSV file
    print("All chunks processed and saved.")