import pandas as pd


def soup_to_df(soup):
    data = []

    table = soup.find('table', attrs={'class': 'soh1'})

    rows = table.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if cols:
            data.append(cols)

    headers = table.find_all('th')

    n_cols = 0
    for header in headers:
        if not header.attrs.get('colspan'):
            n_cols += 1

    col_names = [None for i in range(n_cols)]

    skip_list = []
    counter = 0
    for header in headers:
        if header.attrs.get('colspan'):
            counter += int(header.attrs['colspan'])
            if 'group stage' in header.text:
                last = counter - 1

        elif header.attrs.get('rowspan'):
            col_names[counter] = header.text.strip()
            skip_list.append(counter)
            counter += 1

    sub_headers = headers[len(skip_list) - n_cols:]
    counter = 0
    for sub_header in sub_headers:
        while counter in skip_list:
            counter += 1
        col_names[counter] = sub_header.text.strip()
        skip_list.append(counter)

    return pd.DataFrame(data, columns=col_names), last


def clean_missing(df):
    return df[df['final_line'] != '']
