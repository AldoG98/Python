import requests
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
import random
import os
import logging
from scipy.stats import poisson
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_PATH = r"C:\Users\aldog\OneDrive\Desktop\Liga Mx Program"
API_KEY = "c1b72d5dfdmsh28278028d7dee5ep1c106fjsn91bc37508b33"
API_BASE_URL = "https://api-football-v1.p.rapidapi.com/v3"
LEAGUE_ID = "262"  # Liga MX
SEASON = "2023"

class MatchSimulator:
    def __init__(self, teams, historical_data):
        self.teams = teams
        self.historical_data = historical_data

    def get_team_form(self, team):
        return self.historical_data[team]['form']

    def get_head_to_head(self, team1, team2):
        return self.historical_data[team1]['h2h'][team2]

    def predict_goals(self, team1, team2):
        team1_form = self.get_team_form(team1)
        team2_form = self.get_team_form(team2)
        
        team1_expected_goals = team1_form['avg_goals_scored'] * (1 + team1_form['form_factor'])
        team2_expected_goals = team2_form['avg_goals_scored'] * (1 + team2_form['form_factor'])
        
        return np.random.poisson(team1_expected_goals), np.random.poisson(team2_expected_goals)

    def simulate_match(self, team1, team2):
        team1_goals, team2_goals = self.predict_goals(team1, team2)
        
        return {
            'team1': team1,
            'team2': team2,
            'score': f"{team1_goals}-{team2_goals}",
            'winner': team1 if team1_goals > team2_goals else (team2 if team2_goals > team1_goals else 'Draw'),
            'team1_form': self.get_team_form(team1),
            'team2_form': self.get_team_form(team2),
            'head_to_head': self.get_head_to_head(team1, team2),
            'team1_strength': self.teams[team1]['strength'],
            'team2_strength': self.teams[team2]['strength']
        }

def create_match_report_pdf(prediction, match_week, match_index):
    match_week_dir = os.path.join(BASE_PATH, f'MatchWeek_{match_week}')
    os.makedirs(match_week_dir, exist_ok=True)
    
    filename = os.path.join(match_week_dir, f'Match_{match_index+1}_{prediction["team1"]}_vs_{prediction["team2"]}.pdf')
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph(f"Match Prediction: {prediction['team1']} vs {prediction['team2']}", title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"Predicted Score: {prediction['score']}", styles['Heading2']))
    elements.append(Paragraph(f"Predicted Winner: {prediction['winner']}", styles['Heading3']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Team Strengths", styles['Heading2']))
    strength_data = [
        ['Team', 'Strength Rating'],
        [prediction['team1'], f"{prediction['team1_strength']:.2f}"],
        [prediction['team2'], f"{prediction['team2_strength']:.2f}"]
    ]
    strength_table = Table(strength_data)
    strength_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(strength_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Recent Form", styles['Heading2']))
    form_data = [
        ['Metric', prediction['team1'], prediction['team2']],
        ['Avg Goals Scored', f"{prediction['team1_form']['avg_goals_scored']:.2f}", f"{prediction['team2_form']['avg_goals_scored']:.2f}"],
        ['Avg Goals Conceded', f"{prediction['team1_form']['avg_goals_conceded']:.2f}", f"{prediction['team2_form']['avg_goals_conceded']:.2f}"],
        ['Form Factor', f"{prediction['team1_form']['form_factor']:.2f}", f"{prediction['team2_form']['form_factor']:.2f}"]
    ]
    form_table = Table(form_data)
    form_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(form_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Head-to-Head History", styles['Heading2']))
    h2h = prediction['head_to_head']
    h2h_data = [
        ['Total Matches', str(h2h['total_matches'])],
        [f'{prediction["team1"]} Wins', str(h2h[f'{prediction["team1"]}_wins'])],
        [f'{prediction["team2"]} Wins', str(h2h[f'{prediction["team2"]}_wins'])],
        ['Draws', str(h2h['draws'])],
        ['Avg Goals/Game', f"{h2h['avg_goals_per_game']:.2f}"]
    ]
    h2h_table = Table(h2h_data)
    h2h_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(h2h_table)
    
    try:
        doc.build(elements)
        logger.info(f"Created match report: {filename}")
        print(f"Created match report: {filename}")
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        print(f"Error creating PDF: {e}")

def load_teams():
    try:
        teams_data = fetch_data_from_api("teams", {"league": LEAGUE_ID, "season": SEASON})
        if teams_data:
            return {team['team']['name']: {
                'id': team['team']['id'],
                'strength': random.uniform(0.4, 0.8)
            } for team in teams_data}
    except Exception as e:
        logger.error(f"Error loading teams: {e}")
    return generate_fallback_teams()

def generate_fallback_teams():
    return {
        'América': {'strength': 0.75},
        'Guadalajara': {'strength': 0.70},
        'Cruz Azul': {'strength': 0.68},
        'Pumas UNAM': {'strength': 0.65},
        'Monterrey': {'strength': 0.72},
        'Tigres UANL': {'strength': 0.71},
        'Santos Laguna': {'strength': 0.67},
        'Toluca': {'strength': 0.66},
    }

def fetch_data_from_api(endpoint, params=None):
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
        return None

def load_matches():
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        matches_data = fetch_data_from_api("fixtures", {
            "league": LEAGUE_ID,
            "season": SEASON,
            "from": current_date,
            "to": end_date
        })
        
        if matches_data:
            return [(match['teams']['home']['name'], match['teams']['away']['name']) 
                    for match in matches_data]
        else:
            logger.warning("No matches found for the upcoming week.")
            return []
    except Exception as e:
        logger.error(f"Error loading matches: {e}")
        return []

def load_historical_data():
    teams = load_teams()
    historical_data = {}
    for team in teams:
        historical_data[team] = {
            'form': {
                'avg_goals_scored': random.uniform(0.5, 2.5),
                'avg_goals_conceded': random.uniform(0.5, 2.5),
                'form_factor': random.uniform(-0.2, 0.2)
            },
            'h2h': {other_team: {
                'total_matches': random.randint(10, 30),
                f'{team}_wins': random.randint(3, 12),
                f'{other_team}_wins': random.randint(3, 12),
                'draws': random.randint(2, 8),
                'avg_goals_per_game': round(random.uniform(2.0, 3.5), 2)
            } for other_team in teams if other_team != team}
        }
    return historical_data

def simulate_match_week(simulator, match_week):
    match_week_num = datetime.now().isocalendar()[1]
    
    predictions = []
    for i, (team1, team2) in enumerate(match_week):
        prediction = simulator.simulate_match(team1, team2)
        predictions.append(prediction)
        create_match_report_pdf(prediction, match_week_num, i)
    
    return predictions

def main():
    print("Starting Liga MX match prediction program...")
    teams = load_teams()
    print(f"Loaded {len(teams)} teams.")
    
    historical_data = load_historical_data()
    print("Loaded historical data for teams.")
    
    match_week = load_matches()
    print(f"Loaded {len(match_week)} matches for simulation.")
    
    simulator = MatchSimulator(teams, historical_data)
    predictions = simulate_match_week(simulator, match_week)
    
    print("Match predictions for the upcoming week:")
    for prediction in predictions:
        print(f"{prediction['team1']} vs {prediction['team2']}: {prediction['score']} (Winner: {prediction['winner']})")
    
    print("Program execution completed successfully.")

if __name__ == "__main__":
    main()
