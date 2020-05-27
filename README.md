# Dash Natural Gas Well Production

## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/cygilbert/dash_mobile_games.git
cd dash_mobile_games
pip install -r requirements.txt

```

Run the app

```

python app.py

```

### Get data

```

cd dash_mobile_games/data/get_data

```

Warning: we use selenium to scrap data from [https://www.igdb.com/](https://www.igdb.com/), it requires a special installation and a download of a geockdriver.
More information [there](https://pypi.org/project/selenium/)


## About the app

This Dash app displays an overview about market mobile games (android and iOS). There are filters at the top of the app to update the graphs below. You can also filter date with the histograme. By selecting or hovering over data in scatter plot will update the data table.

Live demo [there](https://dash-mobile-games.herokuapp.com/).

## Date source

- [IGDB](https://www.igdb.com/) for the database game:
    - games list on iOS [here](https://www.igdb.com/platforms/ios/games)
    - game list on Android [here](https://www.igdb.com/platforms/android/games)
- We only kept games still available on stores
- We also delete games with lack of informations

## TODO

- Implement filter on:
    - PEGI
    - Price
- Companies selector is not very precise because we did not find data about connection between big companies and affiliated studios
- Strange lack of games for recent years

## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots

