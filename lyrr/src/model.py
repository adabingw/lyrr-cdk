from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from data import collect
import random
import pathlib

EPOCHS = 15
NAMESPACE = 'adabingw'

def get_model(artist_name): 
    MODEL_NAME = "lyrr-" + artist_name.replace(" ", "").lower()
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    seed_data = random.randint(0,2**32-1)
    training_args = TrainingArguments(
        output_dir="test_trainer",
        overwrite_output_dir=True,
        evaluation_strategy = "epoch",
        learning_rate=1.372e-4,
        weight_decay=0.01,
        num_train_epochs=EPOCHS,
        save_total_limit=10,
        save_strategy='epoch',
        save_steps=1,
        report_to=None,
        seed=seed_data,
        logging_steps=5,
        do_eval=True,
        eval_steps=1,
        load_best_model_at_end=True
        # disable_tqdm=True
        # load_best_model_at_end=True
    )
    
    datasets = collect(artist_name)
    
    if datasets is None:
        return None
    
    def tokenize_function(dataset):
        return tokenizer(dataset["text"])
    
    def group_texts(datasets):
        # concatenate all texts.
        concatenated_examples = {k: sum(datasets[k], []) for k in datasets.keys()}
        total_length = len(concatenated_examples[list(datasets.keys())[0]])
        total_length = (total_length // block_size) * block_size
        
        # split by chunks of max_len.
        result = {
            k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
            for k, t in concatenated_examples.items()
        }
        result["labels"] = result["input_ids"].copy()
        return result
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenized_datasets = datasets.map(tokenize_function, batched=True, num_proc=1, remove_columns=["text"])
    block_size = int(tokenizer.model_max_length / 4)

    lm_datasets = tokenized_datasets.map(
        group_texts,
        batched=True,
        batch_size=1000,
        num_proc=1,
    )
        
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=lm_datasets["train"],
        eval_dataset=lm_datasets["validation"]
    )
    
    trainer.train()
    trainer.save_model(f"./{MODEL_NAME}") 
    
    try: 
        model = AutoModelForCausalLM.from_pretrained(f"{NAMESPACE}/{MODEL_NAME}", cache_dir=pathlib.Path(MODEL_NAME).resolve())
        model = AutoModelForCausalLM.from_pretrained(f"./{MODEL_NAME}") 
        # create repo
        model.push_to_hub(f"{NAMESPACE}/{MODEL_NAME}")
    except: 
        import Exception
        raise Exception("Error in loading model, please ensure that the initial repo is created in the namespace")

    
def generator(text="Salt air", name="lorde"):    
    model = None 
    MODEL_NAME = "lyrr-" + name
    
    try: 
        model = AutoModelForCausalLM.from_pretrained(f"{NAMESPACE}/{MODEL_NAME}", cache_dir=pathlib.Path(MODEL_NAME).resolve())
    except:
        pass
        
    assert model is not None, "error in getting model"
        
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    generated_outputs = model.generate(input_ids, 
                                       max_new_tokens=100,
                                       min_new_tokens=80, 
                                       do_sample=True, 
                                       num_return_sequences=20, 
                                       output_scores=True)    
    generated_decode = tokenizer.decode(generated_outputs[0])
    print(generated_decode)
    
    return generated_decode 
    
if __name__ == "__main__":
    generator()
