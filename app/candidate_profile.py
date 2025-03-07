from file_loader import * 
import json
from constants import * 
from llamaapi import LlamaAPI
from datetime import datetime
import plotly.graph_objects as go
from termcolor import colored

class ProfileAI():

    def __init__(self, resume_parser_api_json_file = RESUME_PARSER_JSON_FILE, llm_api_key = LLM_API_KEY,
                 job_desc_api_json_file = JOBDESC_JSON_FILE,
                 matching_score_api_json_file = MATCHINGSCORE_JSON_FILE,
                 cover_letter_api_json_file = COVER_LETTER_JSON_FILE):
        self.load_config(resume_parser_api_json_file, cover_letter_api_json_file, job_desc_api_json_file, matching_score_api_json_file, llm_api_key)


    def load_api_file(self, api_json_file):
        """
        This function reads the api json files and load them as python variables.

        ----
        input: 
        api_json_file: the json file path

        output:
        api_content: the json file content 
        ---
        """
        with open(api_json_file, 'r') as file:
            api_content = json.load(file)
        return api_content


    def load_config(self, resume_parser_api_json_file, cover_letter_api_json_file, job_desc_api_json_file, matching_score_api_json_file, llm_api_key):
        """
        This function load the configuration that will be used. 
        In particular, it reads the apis, load the LlamaAPI environment and extract today's date.
        
        ---
        input: 
        resume_parser_api_json_file: the json file path for the resume parser instruction json
        cover_letter_api_json_file: the json file path for the cover letter instruction json
        job_desc_api_json_file: the json file path for the job description instruction json
        llm_api_key: the api key from llamaapi.com

        output:
        None.
        ---

        """
        self.llm_api_key = llm_api_key
        self.llama = LlamaAPI(self.llm_api_key)
        self.resume_api_content = self.load_api_file(resume_parser_api_json_file)
        self.jobdesc_api_content = self.load_api_file(job_desc_api_json_file)
        self.matchingscore_api_content = self.load_api_file(matching_score_api_json_file)
        self.cover_letter_api_content = self.load_api_file(cover_letter_api_json_file)
        today = datetime.today()
        formatted_date = today.strftime("%d - %b - %Y")
        self.date_today = formatted_date
    
    
    def connect_resume(self):
        """This function reads the api_content for the resume parsing and add the specific resume information
        
        ---
        input:
        None
        
        output:
        None
        ---
        """
        self.resume_api_content['messages'][0]['content'] = self.resume_api_content['messages'][0]['content'] + '\n Resume:' + self.resume

    def connect_jobdesc(self):
        """This function reads the api_content for the job description parsing and add the specific job description information

        ---
        input:
        None

        output:
        None
        ---
        """
        self.jobdesc_api_content['messages'][0]['content'] = self.jobdesc_api_content['messages'][0][
                                                                'content'] + '\n Job description:' + self.jobdesc

    def profile_candidate(self):
        """
        This function process the resume and store the candidate information in a json file and a string.

        ---
        input:
        None

        output:
        json_content: The profiled (json) version of the resume parsed through the LLM
        ---
        """
        response = self.llama.run(self.resume_api_content)
        success = False
        while not success:
            try:
                profiled_person = response.json()['choices'][0]['message']['content']
                success = True
            except:
                continue
            
        start = profiled_person.find("```json") + len("```json")
        end = profiled_person.find("```", start)
        json_content = profiled_person[start:end].strip()
        self.profile_dict = json.loads(json_content)
        self.profile_str = json_content
        return json_content

    def add_job_description(self, job_description_str = None):
        """Function to add a job description by pasting it into an input prompt.
        ---
        input:
        job_description_str: The input job description.

        output:
        job_description: The input job description is added to the system
        """
        print("Paste the job description below (press Enter twice when done):")
        self.job_description = job_description_str
        return job_description_str
    
    def profile_jobdesc(self):
        """
        This function process the job description and store the information in a json file and a string.

        ---
        input:
        None

        output:
        json_content: The profiled (json) version of the job description parsed through the LLM
        ---
        """
        response = self.llama.run(self.jobdesc_api_content)
        success = False
        while not success:
            try:
                profiled_job = response.json()['choices'][0]['message']['content']
                success = True
            except:
                continue

        start = profiled_job.find("```json") + len("```json")
        end = profiled_job.find("```", start)
        json_content = profiled_job[start:end].strip()
        try:
            # Safely load JSON content
            self.job_dict = json.loads(json_content)
            self.job_str = json_content
            return json_content
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON content: {e}")
            print(f"Raw content: {json_content}")
            self.job_dict = {}
            return {}

    def read_jobdescription_data(self, job_description):
        """
        This function reads the description from the layout and connect it to the resume parser api
        ---
        input:
        job_description: string

        output:
        None
        ---
        """
        self.jobdesc = job_description
        self.connect_jobdesc()

    def read_candidate_data(self, resume_file_path):
        """
        This function reads the resume from the file path and connect it to the resume parser api
        ---
        input:
        resume_file_path: the path where the resume is stored

        output:
        None
        ---
        """
        self.resume_file_path = resume_file_path
        self.resume = read_document(self.resume_file_path)
        self.connect_resume()


    def prepare_cover_letter_api(self):
        """
        This function prepares the cover letter instructions by adding the specific profile information, job description and 
        today's date
        ---
        input:
        None
        
        output:
        None
        ---
        """
        instruction = self.cover_letter_api_content['messages'][0]['content']
        instruction = instruction.replace('{resume_json}', self.profile_str)
        instruction = instruction.replace('{job_description}', self.job_description)
        instruction = instruction.replace('{date}', self.date_today)
        self.cover_letter_api_content['messages'][0]['content'] = instruction

    def prepare_matching_score_api(self):
        """
        This function prepares the matching score instructions by adding the specific profile information, job description and
       getting back the score match, keywords missing and also the tips to improve the resume.
        ---
        input:
        None

        output:
        None
        ---
        """
        instruction = self.matchingscore_api_content['messages'][0]['content']
        instruction = instruction.replace('{resume_json}', self.profile_str)
        instruction = instruction.replace('{job_description}', self.job_str)
        self.matchingscore_api_content['messages'][0]['content'] = instruction

    def write_matching_score(self):
        """
        This function get response on matching score.
        ---
        input:
        None

        output:
        matching_score_response: the 'str' response of the LLM
        ---
        """
        self.prepare_matching_score_api()
        response = self.llama.run(self.matchingscore_api_content)
        #matching_score_response = response.json()
        matching_score_response = response.json()['choices'][0]['message']['content']
        return matching_score_response


    def write_cover_letter(self):
        """
        This function writers the cover letter.
        ---
        input:
        None
        
        output:
        cover_letter_response: the 'str' response of the LLM
        ---
        """
        self.prepare_cover_letter_api()
        response = self.llama.run(self.cover_letter_api_content)
        cover_letter_response = response.json()['choices'][0]['message']['content']
        return cover_letter_response

    def matching_score_visualization(self, similarity_float):
        similarity_percentage = f"{similarity_float:.1f}%"
        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=similarity_float,
            mode="gauge+number",
            title={'text': "Matching percentage (%)"},
            # delta = {'reference': 100},
            gauge={
                'axis': {'range': [0, 100]},
                'steps': [
                    {'range': [0, 50], 'color': "#FFB6C1"},
                    {'range': [50, 70], 'color': "#FFFFE0"},
                    {'range': [70, 100], 'color': "#90EE90"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}}))

        fig.update_layout(width=600, height=400)  # Adjust the width and height as desired
        # fig.show(renderer="browser") # when returning from Gradio interface, there is no need to show here
        # Print notification
        if similarity_float < 50:
            print(colored(f"Low chance ({similarity_percentage}), need to modify your CV!", "red", attrs=["bold"]))
        elif 50 <= similarity_float < 70:
            print(colored(f"Good chance ({similarity_percentage}) but you can improve further!", "yellow",
                          attrs=["bold"]))
        else:
            print(colored(f"Excellent! ({similarity_percentage}) You can submit your CV.", "green", attrs=["bold"]))

        return fig


    



    




    