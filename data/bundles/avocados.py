"""
Example Extension for loading Regional Avocado Price data.
"""
from __future__ import print_function

from cStringIO import StringIO

import requests
import numpy as np
import pandas as pd
from six.moves.urllib_parse import urlencode

from .core import register


def fetch_avocadata(start_date, end_date):
    """Download avocado data to a dataframe.

    Parameters
    ----------
    """
    base_url = 'https://www.marketnews.usda.gov/mnp/fv-report-retail'
    query_params = {
        'class': ['FRUITS'],
        'commodity': ['AVOCADOS'],
        'compareLy': ['No'],
        'endDate': [end_date.strftime("%m/%d/%Y")],
        'format': ['excel'],
        'organic': ['ALL'],
        'portal': ['fv'],
        'region': ['ALL'],
        'repDate': [start_date.strftime("%m/%d/%Y")],
        'type': ['retail'],
    }

    url = base_url + '?' + urlencode(query_params, doseq=1)
    resp = requests.get(url, stream=True)

    resp.raise_for_status()

    f = StringIO()
    for block in resp.iter_content(chunk_size=4096):
        f.write(block)

    f.seek(0)

    frame = pd.read_html(f, header=0)[0]

    # Cleanup
    frame = frame[frame['Unit'] == 'each']
    frame['Organic'] = (frame['Organic'] == 'Y')
    frame['Variety'].replace(
        {'VARIOUS GREENSKIN VARIETIES': 'GREENSKIN'},
        inplace=True,
    )
    frame['Date'] = pd.to_datetime(frame['Date'].values, utc=True)

    frame['Region'] = frame['Region'].str.replace(' U.S.', '')
    frame['Region'] = frame['Region'].str.replace(' ', '_')

    # Drop useless columns.
    return frame.drop(
        ['Class', 'Commodity', 'Environment', 'Unit'],
        axis=1,
    )


@register('avocados',
          calendar_name='Avocalendar',
          start_session=pd.Timestamp('2014-06-02', tz='UTC'),
          end_session=pd.Timestamp('2017-06-01', tz='UTC'))
def ingest(environ,
           asset_db_writer,
           minute_bar_writer,
           daily_bar_writer,
           adjustment_writer,
           calendar,
           start_session,
           end_session,
           cache,
           show_progress,
           output_dir):
    """
    Ingest avocado data.
    """
    try:
        data = cache['avocadata']
    except KeyError:
        data = cache['avocadata'] = fetch_avocadata(start_session, end_session)

    data = data.sort_values(['Region', 'Variety', 'Organic', 'Date'])

    groups = data.groupby(['Region', 'Variety', 'Organic'])

    blocks_by_asset = []
    asset_metadata = []
    for sid, ((region, variety, organic), data) in enumerate(groups, start=1):
        start = data.Date.iloc[0]
        end = data.Date.iloc[-1]

        symbol = '_'.join(map(str, [region, variety[0], str(organic)[0]]))
        asset_metadata.append({
            'sid': sid,
            'symbol': symbol,
            'exchange': 'Avocalendar',
            'start_date': data.Date.iloc[0],
            'end_date': data.Date.iloc[-1],
        })
        print("Ingesting data for: %r" % symbol)

        ohlcv = pd.DataFrame({
            'open': data['Weighted Avg Price'].values,
            'high': data['High Price'].values,
            'low': data['Low Price'].values,
            'close': data['Weighted Avg Price'].values,
            'volume': data['Number of Stores'].values * 1000,
        }, index=data['Date']).reindex(
            calendar.sessions_in_range(start, end),
            method='ffill'
        )

        ohlcv.ffill(inplace=True)

        blocks_by_asset.append((sid, ohlcv))

    asset_db_writer.write(pd.DataFrame.from_records(asset_metadata))
    daily_bar_writer.write(iter(blocks_by_asset))
    # No adjustments.
    adjustment_writer.write()
