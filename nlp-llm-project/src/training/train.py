from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType

model_name = "meta-llama/Llama-2-7b"  # example - pick licensed model
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", load_in_8bit=True) 

lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)

dataset = load_dataset("json", data_files={"train":"data/processed/train.jsonl", "validation":"data/processed/val.jsonl"})
# tokenization function...
def tokenize_fn(examples):
    return tokenizer(examples["input"], truncation=True, padding="max_length", max_length=512)

tokenized = dataset.map(tokenize_fn, batched=True)
training_args = TrainingArguments(
    output_dir="outputs",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    save_strategy="epoch",
    logging_steps=50,
    fp16=True,
)
trainer = Trainer(model=model, args=training_args, train_dataset=tokenized["train"], eval_dataset=tokenized["validation"])
trainer.train()
model.save_pretrained("outputs/lora-adapted")
