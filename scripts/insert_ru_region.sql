INSERT INTO public."region"
(
    country_code,
    country,
    channel_id,
    utc_hour_to_send_day,
    utc_minute_to_send_day,
    intervals_for_good_article,
    main_page_suffix,
    favourite_page_suffix
)
VALUES
(
    'ru',
    'Russian',
    '@wikipedia_daily_ru',
    7,
    0,
    '["9:30", "11:00", "13:30", "15:00", "17:00", "19:00", "22:00"]',
    'Заглавная_страница',
    'Википедия:Избранные_статьи'
);