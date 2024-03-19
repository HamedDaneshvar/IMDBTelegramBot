# ربات تلگرام IMDB

پروژه ربات تلگرام دو زبانه انگلیسی و فارسی که با API The Movie Database (TMDB) برای دریافت اطلاعات فیلم و خزنده برای دریافت لینک دانلود فیلم ادغام شده است. و از MongoDB برای ذخیره داده های دریافتی استفاده می کند، اما لینک های دانلود را به طور موقت و برای یک روز ذخیره می کند

## توضیحات

این پروژه به کاربران اجازه می دهد تا با یک ربات تلگرام که اطلاعات فیلم ها و برنامه های تلویزیونی را با استفاده از داده های TMDB API ارائه می دهد به دو زبان انگلیسی و فارسی تعامل داشته باشند که هنگام استفاده از بات زبان مورد نظر از کاربر پرسیده میشود و ذخیره میشود و هر زمانی که کاربر بخواهد میتواند آن را تغییر دهد. کاربران می توانند فیلم‌ها و سریال‌های تلوزیونی را به چندین صورت جستجو کنند، به صورت استفاده ازنام فیلم یا سریال با دستور /search یا بدون دستور، یا به صورت دریافت اطلاعات فیلم‌ها و سریال های تلوزیونی مشابه به همراه دستور list/ که به صورت لیست به همراه جزئیات به کاربر نمایش داده میشود(در این حالت لینک های دانلود به کاربر نمایش داده نمیشود) و یا به صورت درون خطی که میتوان ربات را مانند ربات های [@gif](https://telegram.me/gif)، [@pic](https://telegram.me/pic)، [@vid](https://telegram.me/vid)  که نمونه‌های بات‌های معروف تلگرام هستند استفاده کرد و جزئیات فیلم را به همراه لینک دانلود(در صورتی که موجود باشد) دریافت کرد. و همچنین کاربر میتواند با استفاده از دستور language/ زبان ربات را تغییر دهد و زبان موردنظر خود را انتخاب کند. به علاوه اینکه دستور help/ نیز برای کاربر تعریف شده که با توجه به زبان ربات تغییر میکند و کاربر میتواند از دکمه menu موجود در بات به آن دست یابد و استفاده کند.
**لازم به ذکر است که این ربات برای اهداف آموزشی نوشته شده وهدف آن نقض کپی رایت نیست و از این بابت هیچ مسئولیتی متوجه ما نخواهد شد.**


## راهنمای شروع

برای شروع پروژه مراحل زیر را دنبال کنید:

### پیش نیازها

- اکانت تلگرام
- API key از سایت [TMDB](themoviedb.org)
- داکر

### نصب

1. باتی را در تلگرام با استفاده از [@botfather](https://t.me/botfather) بسازید و توکن آن را بگیرید
2. حالت inline queries را برای باتتان در [@botfather](https://t.me/botfather) فعال کنید و یک متن نمایشی برای آن انتخاب کنید.
3. حالت inline feedback باتتان را در [@botfather](https://t.me/botfather) فعال کنید.
4. یک اکانت در سایت [themoviedb.org](https://developer.themoviedb.org/docs/getting-started) بساید و از آن API دریافت کنید.
5. چت آیدی تلگرام خود را پیدا کنید. می‌توانید از ربات [@userdatailsbot](https://t.me/userdatailsbot) کمک بگیرید.
6. نام فایل `.env-sample` را به `.env` تغییر دهید.
7. Open the `.env` file and replace the placeholder values with your actual information. Set the `TOKEN` variable to your Telegram bot token. Set `TMDB_API_KEY` and `TMDB_API_READ_ACCESS_TOKEN` to your TMDB API key. Set `DEVELOPER_CHAT_ID` to your Telegram chat ID.
8. فایل `.env` را باز کنید و به جای مقدارهای تستی قرار داده شده، اطلاعات خود را که در قدم های پیش بدست آوردید قرار دهید. مقدار توکن بات خود را برای `TOKEN` قرار دهید. برای `TMDB_API_KEY` و `TMDB_API_READ_ACCESS_TOKEN` نیز مشخصات TMDB API Key که گرفتید را قرار دهید. برای `DEVELOPER_CHAT_ID` نیز چت آیدی اکانت تلگرام خود را قرار دهید.
9.  بعد از اینکه فایل `.env` را با مقادیری که گفتیم بروزرسانی کردید. پروژه را با داکر اجرا کنید.
```sh
docker-compose up --build -d
```
10. بات شما در حال اجراست و می‌توانید از آن استفاده کنید

**Note:** If your bot receives a large amount of traffic and you want to handle it efficiently, it is recommended to deploy the bot with a webhook. This project uses polling for testing purposes.
**توجه:** اگر ربات شما حجم زیادی از ترافیک دریافت می کند و می خواهید آن را به طور موثر مدیریت کنید، توصیه می شود ربات را با یک webhook دپلوی کنید. این پروژه از polling برای اهداف آزمایشی استفاده می کند.

## استفاده

- مکالمه ای را با ربات خود در تلگرام شروع کنید.
- از دستورات و پیام های مختلف برای تعامل با ربات و دریافت اطلاعات درباره فیلم ها و برنامه های تلویزیونی استفاده کنید.

## مشارکت

از مشارکت در پروژه استقبال می شود! اگر ایده، رفع اشکال یا بهبودی دارید، در صورت تمایل یک issue را باز کنید یا یک pull request ارسال کنید.

## لایسنس

این پروژه تحت لایسنس [MIT License](./LICENCE) است.

## سلب مسئولیت

لطفا توجه داشته باشید که این پروژه فقط برای مقاصد آزمایشی و آموزشی است. از آن مسئولانه استفاده کنید و به شرایط و ضوابط خدماتی که با آن ادغام می شود پایبند باشید.

با خیال راحت این فایل README.md را بر اساس جزئیات و الزامات خاص پروژه خود سفارشی کنید. هر بخش یا اطلاعات دیگری را که فکر می کنید به پروژه شما مرتبط است اضافه کنید.


## دمو
به دلیل وجود لینک‌های دانلود و ناقض کپی رایت بودن فیلم در یوتیوب قرار نگرفت و شما می‌توانید آن را دانلود کنید و ببینید. توجه داشته باشید سرعت پاسخدهی کند ربات در فیلم دمو به علت سرعت پایین اینترنت می‌باشد و ربات مشکلی ندارد.

<p align="center">
<a href="Telegram_IMDb_demo_bot.mp4"><img src="video_cover.png" width="80%"></a>
</p>