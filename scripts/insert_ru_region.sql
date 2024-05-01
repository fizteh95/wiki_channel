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
    '["4:00", "6:00", "8:30", "10:00", "12:00", "14:00", "17:00"]',
    'Заглавная_страница',
    'Википедия:Избранные_статьи'
);