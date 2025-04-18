# Setup & Install

Through this guide, you'll see how to setup a complete installation for Bank Track.

## Components

There are 3 external elements that the application need to run:

- a bank data provider - I use GoCardless because it's simple. And free.
- (Optional) a user authentication and management provider - I use Clerk provider.
- a database - I use PostgreSQL.

???+ warning "Disclaimer"
    I have no interests in mentioning any of the previous tecnologies.<br> They are mentionned so anyone can replicate this work.

Let's break down those 3 elements.

### Bank data Provider

A Bank account data provider is a service that let you connect to a bank institution through its service. This way you have a single interface to retrieve bank data such as accounts, balances and transactions.

Most of bank data provider exposes API and sometimes provides some language-specific SDK. To use it, you need to setup an account and generate API keys.

???+ example "If you want to use GoCardless"
    1. You first have to create account [here](https://bankaccountdata.gocardless.com/overview/)
    2. Then generate some API keys on [this page](https://bankaccountdata.gocardless.com/user-secrets/)

    Then you're good to go for now.

### User authentication and management system

User authentication and management was just too much for me. Good and free solutions were out there so I decided to use it instead of reimplementing another buggy solution. You would be able to implement your own one if you want.

???+ example "If you want to use Clerk"
    1. You first have to create account [here](https://dashboard.clerk.com/sign-up?sign_in_force_redirect_url=https://dashboard.clerk.com/&redirect_url=https://clerk.com/)
    2. Then generate some API keys from the Developer section.

    Then you're good to go for now.

### Database

This is the on of the central piecees of the project. I use PostgreSQL because it is the DBMS I used most but the code is agnostic regarding the DBMS. I used Neon.tech to setup a serverless database. They have a free plan that fit my needs.

## Seting up the environment

Once you have those elements, create a `.env` file like below.
```bash title=".env"
ENV=dev
GOC_SECRET_KEY="<GoCardless Secret Key>"
GOC_SECRET_ID="<GoCardless Secret ID>"
CLERK_SECRET_KEY="<Clerk Secret Key>"
CLERK_JWKS_URL="<Clerk JWKS URL>"
DB_ENGINE="postgres" # or any other engine you want
DB_HOST="<host>"
DB_USER="<user>"
DB_PASSWORD="<password>"
DB_DATABASE="<database>"
```
