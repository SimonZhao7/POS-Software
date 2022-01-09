from django.conf import settings
from .models import Date
from .setup import setup_api
from datetime import timedelta

# Global API variable
sheets = setup_api(settings.SCOPES).spreadsheets()

# API Helper methods for working with spreadsheets
def create_spreadsheet():
    spreadsheet_body = {
        'properties': {
            'title': 'Martin POS Spreadsheet'
        }
    }
    return sheets.create(body=spreadsheet_body).execute().get('spreadsheetId')
    
def get_spreadsheet_value(spreadsheet_id, range):
    current_value = sheets.values().get(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueRenderOption='FORMATTED_VALUE'
    ).execute().get('values', [[0]])[0]
    return current_value
    
def save_to_spreadsheet(spreadsheet_id, spreadsheet_range, data, model=None):    
    update_body = {
        'range': spreadsheet_range,
        'values': [data]
    }
        
    sheets.values().update(
        spreadsheetId=spreadsheet_id, 
        range=spreadsheet_range,
        valueInputOption='USER_ENTERED',
        body=update_body
    ).execute()
    return model
    
def fill_missing_dates(current_date, user):
    # Get or create dates
    if Date.objects.exists():
        recent_date = Date.objects.latest('date')
        day_diff = current_date - recent_date.date 
        
        # Fill in the inactive days
        for day in range(day_diff.days):
            new_date = Date.objects.create(
                date=recent_date.date + timedelta(days=1), 
                spreadsheet_row=recent_date.spreadsheet_row + 1
            )
            new_date.save()
            recent_date = save_to_spreadsheet(
                user.spreadsheet_id, 
                'Sheet1!{col}{row}'.format(row=new_date.spreadsheet_row, col='A'),
                [new_date.date.strftime('%m/%d/%Y')],
                new_date
            )
    else:
        recent_date = Date.objects.create(date=current_date, spreadsheet_row=2)
        recent_date.save()
        spreadsheet_range = 'Sheet1!{col}{row}'.format(row=recent_date.spreadsheet_row, col='A')
        save_to_spreadsheet(user.spreadsheet_id, spreadsheet_range, [recent_date.date.strftime('%m/%d/%Y')])
    return recent_date