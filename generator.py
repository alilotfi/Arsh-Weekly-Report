import jdatetime
import locale


def generate(days):
    keys = sorted(days)

    for day in keys:
        locale.setlocale(locale.LC_ALL, "fa_IR")
        jday = jdatetime.date.fromgregorian(date=day)

        print(jday.strftime('%a, %d %b %Y'))
        for event_key in days[day]:
            event = days[day][event_key]
            print(event_key, ':', sep='')
            if 'description' in event:
                for line in event['description']:
                    print(line)
            print('زمان: ', str(event['duration']), sep='')
            if event['done']:
                print('انجام شد')
            elif event['reason']:
                print('دلایل انجام نشدن:', )
                for line in event['reason']:
                    print(line)
            print()
        print()
