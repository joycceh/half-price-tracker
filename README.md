# 🏷️ Half Price Tracker

Woolworths and Coles don't let you track when a specific product goes on sale. The closest feature they offer is a weekly half price catalogue you have to manually scroll through. This tool allows you to paste any Woolworths or Coles product URL, add it to your personal watchlist, and get an email alert automatically when it goes half price.

## Features

- Paste any Woolworths or Coles product URL to add it to your watchlist
- Automatic weekly checks every Wednesday at 9am (after their product prices are updated)
- Email alert when a product hits ~50% off the store's listed original price
- Manual check button to test anytime

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/joycceh/half-price-tracker.git
cd half-price-tracker
```

**2. Create a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root**

Create a file named `.env` and add the following:

```
EMAIL=you@gmail.com
EMAIL_PASSWORD=your16charapppassword
```

To get a Gmail App Password: myaccount.google.com → Security → 2-Step Verification → App Passwords → create one named `half-price-tracker`. This is not your regular Gmail password — it's a separate 16-character password Google generates specifically for apps.

⚠️ Never commit your `.env` file — it's already in `.gitignore`

**5. Run the app**

```bash
python3 api.py
```

Then open `frontend/index.html` in your browser.

## Usage

1. Paste a Woolworths or Coles product URL and click **Add**
2. Enter the email you want alerts sent to and click **Save**
3. Click **Check Now** to test immediately
4. Leave it running — checks automatically every Wednesday at 9am and emails you if anything is half price

Note: The Woolworths and Coles product APIs are undocumented but have been stable for several years. This was validated by open source projects like [aus_grocery_price_database](https://github.com/tjhowse/aus_grocery_price_database) which has been scraping both supermarkets into a timeseries database since 2023.
