import pandas as pd 
import numpy as np 
import requests, json
from pathlib import Path 
from os import listdir
from os.path import isfile, join


# DIALOG ACTION HELPERS

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response




#   CUSTOM FUNCTIONS

def buildTeamDF(teamID):
    fixture_columns = ['fixture_id', 'event_date', 'venue', 'h_team', 'a_team', 'h_halftime_score', 'a_haftime_score', 'h_fulltime_score', 'a_fulltime_score','h_shot_on_goal','a_shot_on_goal','h_shot_off_goal','a_shot_off_goal','h_total_shots','a_total_shots','h_blocked_shots','a_blocked_shots','h_shots_inside_box','a_shots_inside_box','h_shots_outside_box','a_shots_outside_box','h_fouls','a_fouls','h_corner_kicks','a_corner_kicks','h_offsides','a_offsides','h_ball_possession','a_ball_possession','h_yellow_cards','a_yellow_cards','h_red_cards','a_red_cards','h_goalkeeper_saves','a_goalkeeper_saves','h_total_passes','a_total_passes','h_accurate_passes','a_accurate_passes','h_pass_percentage','a_pass_percentage']
    url_addr = f"https://api-football-v1.p.rapidapi.com/v2/fixtures/team/{teamID}/2790"
    headers = {
        'x-rapidapi-key': "3e890f9c4fmshbac87f967184a81p162525jsn1b11c02653ba",
        'x-rapidapi-host': "api-football-v1.p.rapidapi.com"
    }
    raw_data = requests.request("GET", url_addr, headers=headers)
    r_json = raw_data.json()
    fixtures_df = pd.DataFrame(columns=fixture_columns)
    if r_json['api']['results'] != 0:
        for x in range(r_json['api']['results']):
        #just take each item you want and convert it as you need now from json to the dataframe
            fixture_id = r_json['api']['fixtures'][x]['fixture_id']
            url_stats = f"https://api-football-v1.p.rapidapi.com/v2/statistics/fixture/{fixture_id}"
            stat_data = requests.request("GET", url_stats, headers=headers)
            stat_json = stat_data.json()
            if r_json['api']['fixtures'][x]['score']['halftime'] and r_json['api']['fixtures'][x]['score']['fulltime'] != None:
                tdf = {
                    'fixture_id': fixture_id,
                    'event_date': r_json['api']['fixtures'][x]['event_date'],
                    'venue': r_json['api']['fixtures'][x]['venue'],
                    'h_team': r_json['api']['fixtures'][x]['homeTeam']['team_id'],
                    'a_team': r_json['api']['fixtures'][x]['awayTeam']['team_id'],
                    'h_halftime_score': r_json['api']['fixtures'][x]['score']['halftime'].split('-')[0],
                    'a_haftime_score': r_json['api']['fixtures'][x]['score']['halftime'].split('-')[1],
                    'h_fulltime_score': r_json['api']['fixtures'][x]['score']['fulltime'].split('-')[0],
                    'a_fulltime_score': r_json['api']['fixtures'][x]['score']['fulltime'].split('-')[1],
                    'h_shot_on_goal': stat_json['api']['statistics']['Shots on Goal']['home'],
                    'a_shot_on_goal': stat_json['api']['statistics']['Shots on Goal']['away'],
                    'h_shot_off_goal': stat_json['api']['statistics']['Shots off Goal']['home'],
                    'a_shot_off_goal': stat_json['api']['statistics']['Shots off Goal']['away'],
                    'h_total_shots': stat_json['api']['statistics']['Total Shots']['home'],
                    'a_total_shots': stat_json['api']['statistics']['Total Shots']['away'],
                    'h_blocked_shots': stat_json['api']['statistics']['Blocked Shots']['home'],
                    'a_blocked_shots': stat_json['api']['statistics']['Blocked Shots']['away'],
                    'h_shots_inside_box': stat_json['api']['statistics']['Shots insidebox']['home'],
                    'a_shots_inside_box': stat_json['api']['statistics']['Shots insidebox']['away'],
                    'h_shots_outside_box': stat_json['api']['statistics']['Shots outsidebox']['home'],
                    'a_shots_outside_box': stat_json['api']['statistics']['Shots outsidebox']['away'],
                    'h_fouls': stat_json['api']['statistics']['Fouls']['home'],
                    'a_fouls': stat_json['api']['statistics']['Fouls']['away'],
                    'h_corner_kicks': stat_json['api']['statistics']['Corner Kicks']['home'],
                    'a_corner_kicks': stat_json['api']['statistics']['Corner Kicks']['away'],
                    'h_offsides': stat_json['api']['statistics']['Offsides']['home'],
                    'a_offsides': stat_json['api']['statistics']['Offsides']['away'],
                    'h_ball_possession': stat_json['api']['statistics']['Ball Possession']['home'],
                    'a_ball_possession': stat_json['api']['statistics']['Ball Possession']['away'],
                    'h_yellow_cards': stat_json['api']['statistics']['Yellow Cards']['home'],
                    'a_yellow_cards': stat_json['api']['statistics']['Yellow Cards']['away'],
                    'h_red_cards': stat_json['api']['statistics']['Red Cards']['home'],
                    'a_red_cards': stat_json['api']['statistics']['Red Cards']['away'],
                    'h_goalkeeper_saves': stat_json['api']['statistics']['Goalkeeper Saves']['home'],
                    'a_goalkeeper_saves': stat_json['api']['statistics']['Goalkeeper Saves']['away'],
                    'h_total_passes': stat_json['api']['statistics']['Total passes']['home'],
                    'a_total_passes': stat_json['api']['statistics']['Total passes']['away'],
                    'h_accurate_passes': stat_json['api']['statistics']['Passes accurate']['home'],
                    'a_accurate_passes': stat_json['api']['statistics']['Passes accurate']['away'],
                    'h_pass_percentage': stat_json['api']['statistics']['Passes %']['home'],
                    'a_pass_percentage': stat_json['api']['statistics']['Passes %']['away']
                }
                fixtures_df = fixtures_df.append(tdf, ignore_index=True)
            else:
                tdf = {
                    'fixture_id': fixture_id,
                    'h_result': determineIfWinner(h_ft_score, a_ft_score),
                    'event_date': r_json['api']['fixtures'][x]['event_date'],
                    'venue': r_json['api']['fixtures'][x]['venue'],
                    'h_team': r_json['api']['fixtures'][x]['homeTeam']['team_id'],
                    'a_team': r_json['api']['fixtures'][x]['awayTeam']['team_id']
                }
                fixtures_df = fixtures_df.append(tdf, ignore_index=True)
        return fixtures_df.dropna(inplace=True)
    else:
        return 'sorry, no results for that team...'






def getNextFixture(teamID):
    url = f"https://api-football-v1.p.rapidapi.com/v2/fixtures/team/{teamID}/next/1"
    payload={}
    headers = {
    'x-rapidapi-key': '3e890f9c4fmshbac87f967184a81p162525jsn1b11c02653ba'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    r_json = response.json()
    if r_json['api']['results'] != 0:
        fixture = r_json['api']['fixtures'][-1]
        return { 'home_team_id': fixture['homeTeam']['team_id'], 'home_team_name': fixture['homeTeam']['team_name'], 'away_team_id': fixture['awayTeam']['team_id'], 'away_team_name': fixture['awayTeam']['team_name'] }
    else:
        return "sorry, no info..."





def getIdFromName(name):
    file_path = Path('teamIDs.csv')
    teamIDs_df = pd.read_csv(file_path)
    teamIDs_df.set_index("Team", drop=True, inplace=True)
    try:
        return teamIDs_df.loc[name][-1]
    except Exception:
        return "sorry, that doesn't appear to be an EPL team this year"


def getNamefromId(idnum):
    file_path = Path('teamIDs.csv')
    teamIDs_df = pd.read_csv(file_path)
    teamIDs_df.set_index("ID", drop=True, inplace=True)
    try:
        return teamIDs_df.iloc[idnum][-1]
    except Exception:
        return "sorry, that doesn't appear to be an EPL team this year"



def cleanDF(df, id):
    h_drop = ['Unnamed: 0','fixture_id','event_date','venue','a_team','h_team', 'a_haftime_score', 'a_fulltime_score','a_shot_on_goal','a_shot_off_goal','a_total_shots','a_blocked_shots','a_shots_inside_box','a_shots_outside_box','a_fouls','a_corner_kicks','a_offsides','a_ball_possession','a_yellow_cards','a_red_cards','a_goalkeeper_saves','a_total_passes','a_accurate_passes','a_pass_percentage']
    a_drop = ['Unnamed: 0','fixture_id','event_date','venue','h_team','a_team','h_halftime_score', 'h_fulltime_score', 'h_shot_on_goal','h_shot_off_goal','h_total_shots','h_blocked_shots','h_shots_inside_box','h_shots_outside_box','h_fouls','h_corner_kicks','h_offsides','h_ball_possession','h_yellow_cards','h_red_cards','h_goalkeeper_saves','h_total_passes','h_accurate_passes','h_pass_percentage']
    new_columns = ['halftime_score', 'fulltime_score', 'shot_on_goal','shot_off_goal','total_shots','blocked_shots','shots_inside_box','shots_outside_box','fouls','corner_kicks','offsides','ball_possession','yellow_cards','red_cards','goalkeeper_saves','total_passes','accurate_passes','pass_percentage','home_field']
    h_clean_df = df.where(df['h_team'] == id)
    h_clean_df['a_pass_percentage'] = h_clean_df['a_pass_percentage'].str.strip('%')
    h_clean_df['a_ball_possession'] = h_clean_df['a_ball_possession'].str.strip('%')
    h_clean_df.dropna(inplace=True)
    h_clean_df.drop(columns=a_drop, inplace=True)
    a_clean_df = df.where(df['a_team'] == id)
    a_clean_df['a_pass_percentage'] = a_clean_df['a_pass_percentage'].str.strip('%')
    a_clean_df['a_ball_possession'] = a_clean_df['a_ball_possession'].str.strip('%')
    a_clean_df.dropna(inplace=True)
    a_clean_df.drop(columns=a_drop, inplace=True)

    h_clean_df.columns = new_columns
    a_clean_df.columns = new_columns

    return pd.concat([h_clean_df, a_clean_df]).sort_index()



def determineWinner(h_df, a_df, h_id, a_id):
    h_weights = {
        'total_passes': 0.04666782359762534,
        'accurate_passes': 0.04810013821422902,
        'total_shots': 0.03653010460876491,
        'ball_possession': 0.037237171777494416
    }

    a_weights = {
        'total_passes': 0.044189413144872174,
        'accurate_passes': 0.03927389597668354,
        'total_shots': 0.03804805611499009,
        'ball_possession': 0.03754267088918516
    }
    a_tpass_avg = a_df.total_passes.rolling(window=4).mean().iloc[-1]
    a_passacc_avg = a_df.accurate_passes.rolling(window=4).mean().iloc[-1]
    a_tshots_avg = a_df.total_shots.rolling(window=4).mean().iloc[-1]
    a_bposs_avg = a_df.ball_possession.rolling(window=4).mean().iloc[-1]

    h_tpass_avg = h_df.total_passes.rolling(window=4).mean().iloc[-1]
    h_passacc_avg = h_df.accurate_passes.rolling(window=4).mean().iloc[-1]
    h_tshots_avg = h_df.total_shots.rolling(window=4).mean().iloc[-1]
    h_bposs_avg = h_df.ball_possession.rolling(window=4).mean().iloc[-1]

    h_score = (h_tpass_avg * h_weights['total_passes']) + (h_passacc_avg * h_weights['accurate_passes']) + (h_tshots_avg * h_weights['total_shots']) + (h_bposs_avg * h_weights['ball_possession'])

    a_score = (a_tpass_avg * a_weights['total_passes']) + (a_passacc_avg * a_weights['accurate_passes']) + (a_tshots_avg * a_weights['total_shots']) + (a_bposs_avg * a_weights['ball_possession'])

    h_name = getNamefromId(h_id)
    a_name = getNamefromId(a_id)

    if h_score > a_score:
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": f"{h_name} wins!"
            },
        )
    elif a_score > h_score:
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": f"{a_name} wins!"
            },
        )
    else:
        return close(
            intent_request["sessionAttributes"],
            "Fulfilled",
            {
                "contentType": "PlainText",
                "content": 'looks like a draw'
            },
        )




def getPridection(intent_request):
    req_team = get_slots(intent_request)['Teams']
    fixture_info = getNextFixture(getIdFromName(req_team))
    # get season stats
    h_df = buildTeamDF(fixture_info['home_team_id'])
    a_df = buildTeamDF(fixture_info['away_team_id'])
    h_clean = cleanDF(h_df, int(fixture_info['home_team_id']))
    a_clean = cleanDF(a_df, int(fixture_info['away_team_id']))


## Intents Dispatcher
def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']

    if intent_name == 'WhichGame':
        return getPridection(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

# ENTRY POINT

def lambda_handler(event, context):
    
    return dispatch(event)
