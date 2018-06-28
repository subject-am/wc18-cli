#!/usr/bin/env python
import os
import click
import json
import importlib
import sys

#file_dir = os.path.dirname("teamsgroups.py")
file_dir = os.path.dirname(os.path.abspath(__file__)) # pip installs teamsgroups.py on the same directory
sys.path.append(file_dir)
from teamsgroups import Team , Group , LoadTeam ,GetData

def load_json(file):
    """Load JSON file at app start"""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, file)) as jfile:
        data = json.load(jfile)
    return data


TEAM_DATA = load_json("countries.json")["teams"]
COUNTRIES = {team["name"]: team["id"] for team in TEAM_DATA}
GROUPS = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

data = GetData()

# Load Team info for initialation of class

def LoadGroup(letter):
    global data
    matchlist = [match for match in data['groups'][letter]['matches']]
    members = set([match["home_team"] for match in matchlist])
    members = {member: None  for member in list(members)}
    countries = []
    assert len(members.keys()) == 4
    for ID in members.keys():
        for country in data['teams']:
            if ID == country['id']:
                members[ID] = country['name']
    return Group(letter, matchlist, members)
def LoadStats(team):
    global data
    Qualified = None
    GoalCount = 0
    MatchesWon = 0
    MatchesLost = 0
    MatchesTied = 0
    for key in data['groups'].keys():
        if key == team.Group.lower() and data['groups'][key]['winner']:
            if data['groups'][key]['winner'] == team.id or data['groups'][key]['runnerup'] == team.id:
                Qualified = True
            else:
                Qualified = False
    if Qualified == True:
        for key in data['knockout'].keys():
            for match in data['knockout'][key]['matches']:
                if  team.id == match['home_team'] or team.id == match['away_team'] and  match['winner']:
                    if match['winner'] == team.id:
                        Qualified = True
                    else:
                        Qualified = False
                elif team.id == match['home_team'] or team.id == match['away_team']:
                    Qualified = None
    for match in team._Matches:
        if team.id == match['home_team'] and match['home_result'] != None:
            GoalCount += match['home_result']
            if match['home_result'] > match['away_result'] and match['finished'] is True:
                MatchesWon += 1
            elif match['home_result'] < match['away_result'] and match['finished'] is True:
                MatchesLost += 1
            elif match['home_result'] == match['away_result'] and match['finished'] is True:
                MatchesTied +=1
        elif team.id == match['away_team'] and match['away_result'] != None:
            GoalCount += match['away_result']
            if match['home_result'] > match['away_result'] and match['finished'] is True:
                MatchesLost += 1
            elif match['home_result'] < match['away_result'] and match['finished'] is True:
                MatchesWon += 1
            elif match['home_result'] == match['away_result'] and match['finished'] is True:
                MatchesTied +=1
    if Qualified is None:
        Qualified = 'Alive'
    elif Qualified is True:
        Qualified = 'Passed'
    else:
        Qualified = 'Eliminated'
    return {
    'Status': Qualified,
    'Goals': GoalCount,
    'Matches Won': MatchesWon,
    'Matches Lost': MatchesLost,
    'Matches Tied': MatchesTied
    }


@click.command()
@click.option('--country', type=click.Choice(COUNTRIES.keys()), help='Show the stats of the country and soonest match')
# @click.option('--group', type=click.Choice(COUNTRIES.keys()), help='Show the stats of the country and its matches')
@click.option('--allmatches', default=False ,help='Show the stats plus all the matches of the team')
@click.option('--group', help="Show group table", type=click.Choice(GROUPS))
def main(country, allmatches, group):
    global data
    if country and allmatches:
        team = LoadTeam(Country=country, Data=data)
        stats = LoadStats(team)
        team.LoadMatches()
        print("--------------------------------------------------------------")
        click.echo('TEAM: ' + click.style(f'{team.Nation}', fg="magenta", bold=True))
        click.echo('GROUP: ' + click.style(f'{team.Group}', fg="yellow"))
        click.echo('SOONEST MATCH:' + click.style(f'{team.SoonestMatch}', fg="green"))
        click.echo('STATISTICS:')
        if stats['Status'] is 'Alive':
            click.echo('    Status:' + click.style(stats['Status'], fg='green'))
        else:
            click.echo('    Status: ' +
             click.style(stats['Status'], fg='red'))
        click.echo('    Goals: ' + click.style(str(stats['Goals']), fg="red", blink=True))
        click.echo('    Matches Won: ' +
         click.style(str(stats['Matches Won']), fg="yellow", bold=True))
        click.echo('    Matches Lost: ' +
         click.style(str(stats['Matches Lost']), fg="cyan", bold=True))
        click.echo('    Matches Tied: ' +
         click.style(str(stats['Matches Tied']) , bold=True))
        click.echo(click.style('\n MATCHES: ', fg='red') +
         f' \n {" ".join(x for x in team.Matches)}')
        print("--------------------------------------------------------------")
    elif country:
        team = LoadTeam(Country=country, Data=data)
        stats = LoadStats(team)
        team.LoadMatches()
        print("--------------------------------------------------------------")
        click.echo('TEAM: ' +
         click.style(f'{team.Nation}', fg="magenta", bold=True))
        click.echo('GROUP: ' +
         click.style(f'{team.Group}',fg="yellow"))
        click.echo('SOONEST MATCH: ' + click.style(f'{team.SoonestMatch}', fg="green"))
        click.echo('STATISTICS:')
        if stats['Status'] is 'Alive':
            click.echo('    *Status:' +
             click.style(stats['Status'], fg='green'))
        else:
            click.echo('    *Status: ' +
             click.style(stats['Status'], fg='red'))
        click.echo('    *Goals: ' +
         click.style(str(stats['Goals']),fg="red", blink=True))
        click.echo('    *Matches Won: ' +
         click.style(str(stats['Matches Won']),fg="yellow", bold=True))
        click.echo('    *Matches Lost: ' +
            click.style(str(stats['Matches Lost']), fg="cyan", bold=True))
        click.echo('    Matches Tied: ' +
         click.style(str(stats['Matches Tied']) , bold=True))
        print("--------------------------------------------------------------")
    elif group:
        Group = LoadGroup(group)
        click.secho(Group.group_table_as_str(), fg="green")
        click.echo()

if __name__ == '__main__':
    main()
