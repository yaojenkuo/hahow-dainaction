import pandas as pd
import matplotlib.pyplot as plt

class KaggleSurvey2020:
    """
    This class helps us analyze the Kaggle Survey 2020 with ease.
    See https://www.kaggle.com/c/kaggle-survey-2020
    Args:
        csv_file (str): Specify the file path of kaggle_survey_2020_responses.csv.
    """
    def __init__(self, csv_file):
        self._csv_file = csv_file
        # import survey responses
        survey_response = pd.read_csv(self._csv_file, skiprows=[1])
        survey_response = survey_response.drop('Time from Start to Finish (seconds)', axis=1)
        # import survey questions
        first_2_rows = pd.read_csv(self._csv_file, nrows=1)
        question_desc = first_2_rows.values.ravel()[1:]
        question_index = first_2_rows.columns[1:]
        questions_ser = pd.Series(question_desc, index=question_index)
        self._survey_response = survey_response
        self._questions_ser = questions_ser
    def generate_questions(self):
        """
        This function returns the DataFrame of questions.
        """
        question_indices = [l[0] + l[1] if len(l) > 1 else l[0] for l in self._questions_ser.index.str.split("_")]
        question_indices = [s.replace('Part', '') if 'Part' in s else s for s in question_indices]
        question_indices = [s.replace('OTHER', '') if 'OTHER' in s else s for s in question_indices]
        questions = pd.DataFrame()
        questions['question_index'] = question_indices
        questions['question_desc'] = self._questions_ser.values
        return questions
    def generate_unique_questions(self):
        """
        This function returns the DataFrame of unique questions.
        """
        questions = self.generate_questions()
        question_indices = questions['question_index'].values
        question_descs = [l[0] for l in self._questions_ser.str.split(' - ')]
        # Collecting unique questions indices and descriptions
        unique_question_indices = []
        unique_question_descs = []
        for qi, qd in zip(question_indices, question_descs):
            if qi not in unique_question_indices:
                unique_question_indices.append(qi)
            if qd not in unique_question_descs:
                unique_question_descs.append(qd)
        # Categorizing question type
        question_types = ['multiple selection' if 'Select all that apply' in s else 'multiple choice' for s in unique_question_descs]
        unique_questions = pd.DataFrame()
        unique_questions['question_index'] = unique_question_indices
        unique_questions['question_desc'] = unique_question_descs
        unique_questions['question_type'] = question_types
        return unique_questions
    def summarize_response(self, question_index):
        """
        This function returns the summary of a given question.
        Args:
            question_index (str): Specify the question, e.g. 'Q1' for Question 1, 'Q26A' for Question 26-A.
        """
        questions = self.generate_questions()
        column_iloc = questions[questions['question_index'] == question_index].index
        ith_question = self._survey_response.iloc[:, column_iloc]
        unique_questions = self.generate_unique_questions()
        ith_unique_question = unique_questions[unique_questions['question_index'] == question_index]
        question_desc = ith_unique_question['question_desc'].values[0]
        print(question_desc)
        # Use simple value_counts for multiple choice questions
        if column_iloc.size == 1:
            summary = ith_question[question_index].value_counts(normalize=True).sort_values()
        # Use iteration for multiple selection questions
        else:
            freq_counts = dict()
            for col in ith_question.columns:
                ser = ith_question[col]
                ser_value_counts = ser.value_counts()
                k, v = ser_value_counts.index[0], ser_value_counts.values[0]
                freq_counts[k] = v
            summary = pd.Series(freq_counts).sort_values()
        return summary
    def plot_summary(self, question_index):
        """
        This function plots the bar plot of a given question.
        Args:
            question_index (str): Specify the question, e.g. 'Q1' for Question 1, 'Q26A' for Question 26-A.
        """
        fig = plt.figure()
        axes = plt.axes()
        response_ser = self.summarize_response(question_index)
        # Showing only top 10 categories if there are too many.
        if response_ser.size > 10:
            print("Too many categories, only showing the top 10.")
            top_ten = response_ser[-10:]
            y = top_ten.index
            width = top_ten.values
        else:
            y = response_ser.index
            width = response_ser.values
        # Highlight top 3 with red
        colors = ['c' for _ in range(y.size)]
        colors[-3:] = ['r', 'r', 'r']
        axes.barh(y, width, color=colors)
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        axes.tick_params(length=0)
        unique_questions = self.generate_unique_questions()
        ith_unique_question = unique_questions[unique_questions['question_index'] == question_index]
        question_desc = ith_unique_question['question_desc'].values[0]
        axes.set_title(question_desc)
        plt.show()