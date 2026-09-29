import requests, duckdb, tempfile, os
from dataset.cleanup import clean_chatml_entry

url = 'https://huggingface.co/datasets/HuggingFaceH4/deita-10k-v0-sft/resolve/main/data/train_sft-00000-of-00001.parquet'
print("Fetching parquet...")
resp = requests.get(url)
tmp_p = "tmp_deita.parquet"
with open(tmp_p, "wb") as f:
    f.write(resp.content)

try:
    df = duckdb.query(f"SELECT * FROM read_parquet('{tmp_p}')").df()
    print("Total rows in train_sft:", len(df))
    valid = 0
    for _, row in df.iterrows():
        d = row.to_dict()
        msgs = d.get("messages")
        if msgs is not None and hasattr(msgs, "__iter__"):
            d["messages"] = list(msgs)
        c = clean_chatml_entry(d)
        if c:
            valid += 1
    print("Valid ChatML entries:", valid)
finally:
    if os.path.exists(tmp_p):
        os.remove(tmp_p)
