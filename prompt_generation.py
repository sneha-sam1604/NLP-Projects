import argparse
import os
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer, pipeline

### using GPU if available
device = torch.device(torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
torch.manual_seed(1000)

RELATIONS = {
    "CountryBordersWithCountry",
    "RiverBasinsCountry",
    "PersonLanguage",
    "PersonProfession",
    "PersonInstrument"
}

def initialize_lm(model_type, top_k):
    ### using the HuggingFace pipeline to initialize the model and its corresponding tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_type)
    model = AutoModelForMaskedLM.from_pretrained(model_type).to(device)
    device_id = (
        -1 if device == torch.device("cpu") else 0
    )  ### -1 device is for cpu, 0 for gpu
    nlp = pipeline(
        "fill-mask", model=model, tokenizer=tokenizer, top_k=top_k, device=device_id
    )  ### top_k defines the number of ranked output tokens to pick in the [MASK] position
    return nlp, tokenizer.mask_token

def create_prompt(subject_entity, relation, mask_token):
    ### depending on the relation, we fix the prompt
    if relation == "CountryBordersWithCountry":
        # prompt = f"{subject_entity} shares border with {mask_token}."
        # prompt = f"{subject_entity} is surrounded by {mask_token}."
        prompt = f"The neighbouring country of {subject_entity} is {mask_token}."
    elif relation == "RiverBasinsCountry":
        # prompt = f"{subject_entity} river basins in {mask_token}."
        prompt = f"{subject_entity} river is a river basin in the country {mask_token}."
        # prompt = f"The source of {subject_entity} lies in {mask_token}."
    elif relation == "PersonLanguage":
        prompt = f"{subject_entity} speaks in {mask_token}."
        # prompt = f"{subject_entity} speaks {mask_token}."
        # prompt = f"{subject_entity} speaks in {mask_token} language."
    elif relation == "PersonProfession":
        prompt = f"{subject_entity} is a {mask_token} by profession."
        # prompt = f"{subject_entity} works as a {mask_token}."
        # prompt = f"{subject_entity} is a {mask_token}."
        # prompt = f"The profession of {subject_entity} is {mask_token}."
    elif relation == "PersonInstrument":
        prompt = f"{subject_entity} plays {mask_token}, which is an instrument."
        # prompt = f"{subject_entity} plays musical instruments like {mask_token}."
        # prompt = f"{subject_entity} plays an instrument called {mask_token}."
    return prompt

def probe_lm(model_type, top_k, relation, subject_entities, output_dir: Path):
    
    ### initializing the language model
    nlp, mask_token = initialize_lm(model_type, top_k) 
        
    ### for every subject-entity in the entities list, we probe the LM using the below sample prompts
    results = []
    for subject_entity in subject_entities:
        print(
            "Probing the {} language model for {} (subject-entity) and {} relation".format(
                model_type, subject_entity, relation
            )
        )
        prompt = create_prompt(subject_entity, relation, mask_token) ### creating a specific prompt for the given relation
        probe_outputs = nlp(prompt) ### probing the language model and obtaining the ranked tokens in the masked_position

        ### saving the top_k outputs and the likelihood scores received with the sample prompt
        for sequence in probe_outputs:
            results.append(
                {
                    "Prompt": prompt,
                    "SubjectEntity": subject_entity,
                    "Relation": relation,
                    "ObjectEntity": sequence["token_str"],
                    "Probability": round(sequence["score"], 4),
                }
            )

    ### saving the prompt outputs separately for each relation type
    results_df = pd.DataFrame(results).sort_values(
        by=["SubjectEntity", "Probability"], ascending=(True, False)
    )

    if output_dir.exists():
        assert output_dir.is_dir()
    else:
        output_dir.mkdir(exist_ok=True, parents=True)

    results_df.to_csv(output_dir / f"{relation}.csv", index=False)


def your_solution(input_dir, prob_threshold, relations, output_dir: Path):
    print("Running the your_solution method ...")

    ### for each relation, we run the your_solution method
    for relation in relations:
        df = pd.read_csv(input_dir / f"{relation}.csv")
        # df = df[
        #     df["Probability"] >= prob_threshold
        # ]  ### all the output tokens with >= 0.5 likelihood are chosen and the rest are discarded

        df.loc[df['Probability'] >= prob_threshold[0], 'greaterThanThresh'] = True
        df.loc[df['Probability'] < prob_threshold[0], 'lessThanThresh'] = True
        
        if len(df.loc[df["greaterThanThresh"] == True]):
            df = df[df["Probability"] >= prob_threshold[0]]
        else:
            df = df[df["Probability"] >= prob_threshold[1]]

        if output_dir.exists():
            assert output_dir.is_dir()
        else:
            output_dir.mkdir(exist_ok=True, parents=True)

        df.to_csv(
            output_dir / f"{relation}.csv", index=False
        )  ### save the selected output tokens separately for each relation


def main():
    parser = argparse.ArgumentParser(
        description="Probe a Language Model and Run the Solution Method on Prompt Outputs"
    )
    parser.add_argument(
        "--model_type",
        type=str,
        default="bert-base-uncased",
        help="HuggingFace model name",
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        default="./dataset/test/",
        help="input directory containing the subject-entities for each relation to probe the language model",
    )
    parser.add_argument(
        "--prompt_output_dir",
        type=str,
        default="./prompt_output_bert_base_uncased/",
        help="output directory to store the prompt output",
    )
    parser.add_argument(
        "--solution_output_dir",
        type=str,
        default="./solution/",
        help="output directory to store the solution output",
    )
    args = parser.parse_args()
    print(args)

    model_type = args.model_type
    input_dir = Path(args.input_dir)
    prompt_output_dir = Path(args.prompt_output_dir)
    solution_output_dir = Path(args.solution_output_dir)

    top_k =200  ### picking the top 200 ranked prompt outputs in the [MASK] position

    ### call the prompt function to get output for each (subject-entity, relation)
    for relation in RELATIONS:
        entities = (
            pd.read_csv(input_dir / f"{relation}.csv")["SubjectEntity"]
            .drop_duplicates(keep="first")
            .tolist()
        )
        probe_lm(model_type, top_k, relation, entities, prompt_output_dir)

    prob_threshold = [0.3, 0.1] ### setting the threshold to select the output tokens
    # prob_threshold = 0.3
    
    ### run the your_solution method on the prompt outputs
    your_solution(prompt_output_dir, prob_threshold, RELATIONS, solution_output_dir)


if __name__ == "__main__":
    main()

#References:
#https://datatofish.com/if-condition-in-pandas-dataframe/
