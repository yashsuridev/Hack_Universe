from typing import Dict, List, Optional, Set
import re
from app.utils.logging import get_logger

logger = get_logger(__name__)


POPULAR_NPM_PACKAGES = {
    'lodash', 'react', 'react-dom', 'express', 'axios', 'moment', 'chalk',
    'commander', 'debug', 'async', 'request', 'underscore', 'jquery',
    'webpack', 'babel', 'eslint', 'prettier', 'typescript', 'jest',
    'mocha', 'chai', 'sinon', 'enzyme', 'testing-library', 'cypress',
    'next', 'nuxt', 'gatsby', 'vite', 'rollup', 'parcel', 'snowpack',
    'tailwindcss', 'styled-components', 'emotion', 'material-ui', 'antd',
    'bootstrap', 'rxjs', 'redux', 'mobx', 'zustand', 'recoil', 'jotai',
    'socket.io', 'ws', 'fastify', 'koa', 'hapi', 'nest', 'adonis',
    'prisma', 'typeorm', 'sequelize', 'mongoose', 'knex', 'objection',
    'passport', 'jsonwebtoken', 'bcrypt', 'helmet', 'cors', 'compression',
    'dotenv', 'config', 'nconf', 'convict', 'joi', 'yup', 'zod',
    'date-fns', 'dayjs', 'luxon', 'moment-timezone', 'timezone',
    'uuid', 'nanoid', 'shortid', 'cuid', 'ulid',
    'ramda', 'fp-ts', 'neverthrow', 'result-type', 'ts-results',
    'class-validator', 'class-transformer', 'reflect-metadata',
    'rxjs', 'zen-observable', 'xstate', 'robot3', 'machina',
    'framer-motion', 'react-spring', 'animejs', 'gsap', 'lottie',
    'three', 'babylonjs', 'pixi.js', 'phaser', 'melonjs',
    'chart.js', 'd3', 'recharts', 'victory', 'nivo', 'visx',
    'swr', 'react-query', 'rtk-query', 'urql', 'apollo-client',
    'graphql', 'graphql-tools', 'prisma', 'typegraphql', 'nexus',
    'fastify', 'express', 'koa', 'hapi', 'nest', 'adonis', 'feathers',
    'socket.io', 'ws', 'uws', 'ws', 'engine.io', 'primus',
    'mongoose', 'typeorm', 'prisma', 'sequelize', 'knex', 'objection',
    'redis', 'ioredis', 'bull', 'agenda', 'cron', 'node-cron',
    'winston', 'pino', 'bunyan', 'loglevel', 'debug', 'consola',
    'jest', 'mocha', 'jasmine', 'ava', 'tape', 'tap', 'uvu',
    'cypress', 'playwright', 'puppeteer', 'testcafe', 'webdriverio',
    'eslint', 'prettier', 'typescript', 'babel', 'webpack', 'vite',
    'rollup', 'parcel', 'esbuild', 'swc', 'tsc', 'ts-node',
    'nodemon', 'pm2', 'forever', 'supervisor', 'node-dev',
    'husky', 'lint-staged', 'commitlint', 'standard', 'xo',
    'npm', 'yarn', 'pnpm', 'npm-check-updates', 'depcheck',
    'lodash', 'underscore', 'ramda', 'rxjs', 'bluebird', 'q',
    'axios', 'request', 'superagent', 'got', 'ky', 'node-fetch',
    'express', 'koa', 'fastify', 'hapi', 'restify', 'polka',
    'mongoose', 'sequelize', 'typeorm', 'prisma', 'waterline',
    'redis', 'memcached', 'amqplib', 'kafkajs', 'nats',
    'dockerode', 'kubernetes-client', 'helm', 'kubectl',
    'aws-sdk', '@aws-sdk', 'google-cloud', '@google-cloud', 'azure',
    'firebase', 'supabase', 'appwrite', 'pocketbase',
    'stripe', 'paypal', 'braintree', 'adyen', 'square',
    'sendgrid', 'mailgun', 'postmark', 'nodemailer', 'mailer',
    'twilio', 'nexmo', 'plivo', 'vonage', 'messagebird',
    'sentry', 'rollbar', 'bugsnag', 'airbrake', 'honeybadger',
    'datadog', 'newrelic', 'elastic-apm', 'prometheus', 'grafana',
    'prom-client', 'statsd', 'telegraf', 'influxdb', 'timescaledb',
    'pg', 'mysql2', 'sqlite3', 'better-sqlite3', 'tedious',
    'mongodb', 'mongoose', 'redis', 'ioredis', 'cassandra-driver',
    'neo4j', 'orientdb', 'arangodb', 'couchdb', 'pouchdb',
    'graphql', 'apollo-server', 'express-graphql', 'graphql-yoga',
    'grpc', '@grpc', 'protobufjs', 'protobuf', 'protobuf.ts',
    'web3', 'ethers', 'viem', 'wagmi', 'rainbowkit', 'web3modal',
    'solana', '@solana', 'anchor', 'spl-token', 'metaplex',
    'next', 'nuxt', 'gatsby', 'remix', 'astro', 'sveltekit',
    'react', 'vue', 'svelte', 'solid', 'preact', 'lit', 'alpine',
    'tailwindcss', 'styled-components', 'emotion', 'jss', 'aphrodite',
    'bootstrap', 'bulma', 'foundation', 'semantic-ui', 'materialize',
    'antd', 'mui', 'chakra-ui', 'radix', 'headlessui', 'reach-ui',
    'formik', 'react-hook-form', 'react-final-form', 'unform',
    'yup', 'zod', 'joi', 'superstruct', 'io-ts', 'runtypes',
    'zustand', 'redux', 'mobx', 'recoil', 'jotai', 'valtio',
    'react-query', 'swr', 'rtk-query', 'urql', 'apollo-client',
    'axios', 'ky', 'got', 'superagent', 'node-fetch', 'fetch',
    'date-fns', 'dayjs', 'luxon', 'moment', 'date-fns-tz',
    'uuid', 'nanoid', 'cuid', 'ulid', 'shortid', 'ksuid',
    'lodash', 'ramda', 'rxjs', 'fp-ts', 'neverthrow', 'effect',
    'class-validator', 'class-transformer', 'typeorm', 'mikro-orm',
    'nest', 'fastify', 'express', 'koa', 'hapi', 'adonis', 'feathers',
    'socket.io', 'ws', 'uws', 'engine.io', 'primus', 'faye',
    'bull', 'agenda', 'cron', 'node-cron', 'bree', 'later',
    'winston', 'pino', 'bunyan', 'consola', 'signale', 'tracer',
    'jest', 'vitest', 'mocha', 'jasmine', 'ava', 'tape', 'uvu',
    'cypress', 'playwright', 'puppeteer', 'testcafe', 'webdriverio',
    'eslint', 'prettier', 'stylelint', 'typescript', 'babel', 'swc',
    'webpack', 'vite', 'rollup', 'esbuild', 'parcel', 'snowpack',
    'nodemon', 'ts-node', 'tsx', 'concurrently', 'cross-env',
    'husky', 'lint-staged', 'commitlint', 'standard', 'xo', 'eslint-plugin',
}

POPULAR_PYPI_PACKAGES = {
    'requests', 'django', 'flask', 'fastapi', 'numpy', 'pandas',
    'matplotlib', 'scipy', 'scikit-learn', 'tensorflow', 'torch',
    'pillow', 'beautifulsoup4', 'lxml', 'sqlalchemy', 'alembic',
    'celery', 'redis', 'psycopg2', 'pymongo', 'boto3', 'google-cloud',
    'azure', 'firebase', 'supabase', 'stripe', 'twilio', 'sendgrid',
    'pytest', 'unittest', 'mock', 'factory-boy', 'faker', 'hypothesis',
    'black', 'flake8', 'mypy', 'isort', 'bandit', 'safety',
    'uvicorn', 'gunicorn', 'hypercorn', 'daphne', 'uvloop',
    'click', 'typer', 'rich', 'tqdm', 'colorama', 'termcolor',
    'pydantic', 'marshmallow', 'attrs', 'dataclasses', 'typing-extensions',
    'httpx', 'aiohttp', 'websockets', 'socketio', 'python-socketio',
    'jinja2', 'mako', 'cheetah', 'genshi', 'django-template',
    'cryptography', 'pyjwt', 'passlib', 'bcrypt', 'argon2',
    'python-dotenv', 'configparser', 'toml', 'yaml', 'json5',
    'urllib3', 'certifi', 'charset-normalizer', 'idna', 'requests-toolbelt',
    'openpyxl', 'xlrd', 'xlwt', 'csv', 'json', 'xml', 'html',
    'paramiko', 'fabric', 'invoke', 'ssh', 'scp', 'sftp',
    'schedule', 'apscheduler', 'croniter', 'python-crontab',
    'loguru', 'structlog', 'python-json-logger', 'sentry-sdk',
    'prometheus-client', 'statsd', 'datadog', 'newrelic', 'elastic-apm',
    'sqlalchemy', 'django-orm', 'peewee', 'pony', 'tortoise-orm',
    'alembic', 'migrate', 'db-migrate', 'flyway', 'liquibase',
    'celery', 'rq', 'huey', 'dramatiq', 'arq', 'taskiq',
    'redis', 'redis-py', 'aioredis', 'redis-om', 'redisearch',
    'elasticsearch', 'opensearch', 'solr', 'whoosh', 'meilisearch',
    'kafka', 'confluent-kafka', 'aiokafka', 'pulsar', 'nats',
    'grpc', 'protobuf', 'thrift', 'avro', 'msgpack', 'capnp',
    'fastapi', 'starlette', 'quart', 'sanic', 'aiohttp', 'tornado',
    'django', 'flask', 'bottle', 'falcon', 'hug', 'cherrypy',
    'pytest', 'unittest', 'nose', 'tox', 'coverage', 'pytest-cov',
    'black', 'isort', 'flake8', 'mypy', 'pylint', 'bandit', 'safety',
    'poetry', 'pipenv', 'pipx', 'pdm', 'hatch', 'rye', 'uv',
    'setuptools', 'wheel', 'build', 'twine', 'pip', 'pip-tools',
    'virtualenv', 'venv', 'conda', 'mamba', 'micromamba', 'pixi',
    'docker', 'docker-compose', 'kubernetes', 'helm', 'kubectl',
    'terraform', 'pulumi', 'crossplane', 'argo', 'flux',
    'ansible', 'salt', 'fabric', 'invoke', 'paramiko', 'ssh',
    'prometheus', 'grafana', 'alertmanager', 'pushgateway', 'node-exporter',
    'opentelemetry', 'jaeger', 'zipkin', 'tempo', 'loki',
    'sentry', 'rollbar', 'bugsnag', 'airbrake', 'honeybadger',
    'datadog', 'newrelic', 'elastic-apm', 'signoz', 'uptrace',
    'stripe', 'paypal', 'braintree', 'adyen', 'square', 'checkout',
    'sendgrid', 'mailgun', 'postmark', 'mailjet', 'sparkpost',
    'twilio', 'nexmo', 'plivo', 'vonage', 'messagebird', 'telnyx',
    'firebase', 'supabase', 'appwrite', 'pocketbase', 'nocoDB',
    'prisma', 'typeorm', 'sequelize', 'mongoose', 'knex', 'objection',
    'graphql', 'apollo', 'graphql-core', 'strawberry', 'ariadne',
    'websocket', 'websockets', 'socketio', 'asyncio', 'uvloop',
    'multiprocessing', 'threading', 'concurrent', 'asyncio',
    'pathlib', 'os', 'sys', 'json', 'csv', 'xml', 'html',
    're', 'datetime', 'time', 'calendar', 'collections',
    'itertools', 'functools', 'operator', 'decimal', 'fractions',
    'random', 'secrets', 'hashlib', 'hmac', 'base64', 'binascii',
    'urllib', 'http', 'socket', 'ssl', 'email', 'mimetypes',
    'logging', 'argparse', 'configparser', 'tomllib', 'tomli',
    'yaml', 'json5', 'msgpack', 'cbor', 'pickle', 'shelve',
    'sqlite3', 'dbm', 'gdbm', 'bsddb', 'dumbdbm', 'anydbm',
    'csv', 'tsv', 'excel', 'openpyxl', 'xlrd', 'xlwt', 'pandas',
    'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh',
    'pillow', 'opencv', 'scikit-image', 'imageio', 'PIL',
    'requests', 'httpx', 'aiohttp', 'urllib3', 'urllib', 'http',
    'beautifulsoup4', 'lxml', 'html5lib', 'cssselect', 'pyquery',
    'scrapy', 'playwright', 'selenium', 'puppeteer', 'splash',
    'fastapi', 'starlette', 'django', 'flask', 'bottle', 'falcon',
    'pydantic', 'marshmallow', 'attrs', 'dataclasses', 'typing',
    'sqlalchemy', 'alembic', 'django-orm', 'peewee', 'pony',
    'celery', 'rq', 'huey', 'dramatiq', 'arq', 'taskiq',
    'redis', 'aioredis', 'redis-om', 'redisearch', 'redis-py',
    'elasticsearch', 'opensearch', 'solr', 'whoosh', 'meilisearch',
    'kafka', 'confluent-kafka', 'aiokafka', 'pulsar', 'nats',
    'grpc', 'protobuf', 'thrift', 'avro', 'msgpack', 'capnp',
    'pytest', 'unittest', 'nose', 'tox', 'coverage', 'pytest-cov',
    'black', 'isort', 'flake8', 'mypy', 'pylint', 'bandit', 'safety',
    'poetry', 'pipenv', 'pipx', 'pdm', 'hatch', 'rye', 'uv',
    'setuptools', 'wheel', 'build', 'twine', 'pip', 'pip-tools',
}

POPULAR_PACKAGES = {
    'npm': POPULAR_NPM_PACKAGES,
    'pypi': POPULAR_PYPI_PACKAGES,
}


class TyposquattingDetector:
    def __init__(self):
        self.popular_packages = POPULAR_PACKAGES
    
    def check(self, package_name: str, ecosystem: str) -> Optional[Dict]:
        popular = self.popular_packages.get(ecosystem, set())
        if not popular:
            return None
        
        if package_name in popular:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        for popular_pkg in popular:
            similarity = self._calculate_similarity(package_name, popular_pkg)
            if similarity > best_similarity and similarity >= 0.7:
                best_similarity = similarity
                best_match = popular_pkg
        
        if best_match and best_similarity >= 0.7:
            return {
                'similar_to': best_match,
                'similarity': best_similarity,
                'package': package_name,
                'ecosystem': ecosystem,
                'detection_method': 'string_similarity',
            }
        
        return self._check_common_patterns(package_name, ecosystem)
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        if s1 == s2:
            return 1.0
        
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        distance = dp[len1][len2]
        max_len = max(len1, len2)
        return 1.0 - (distance / max_len)
    
    def _check_common_patterns(self, package_name: str, ecosystem: str) -> Optional[Dict]:
        patterns = [
            (r'^(.+)-js$', r'\1'),
            (r'^(.+)\.js$', r'\1'),
            (r'^(.+)-py$', r'\1'),
            (r'^(.+)\.py$', r'\1'),
            (r'^(.+)-ts$', r'\1'),
            (r'^(.+)\.ts$', r'\1'),
            (r'^(.+)-lib$', r'\1'),
            (r'^lib-(.+)$', r'\1'),
            (r'^(.+)-utils$', r'\1'),
            (r'^utils-(.+)$', r'\1'),
            (r'^(.+)-core$', r'\1'),
            (r'^core-(.+)$', r'\1'),
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, package_name)
            if match:
                base_name = match.group(1)
                popular = self.popular_packages.get(ecosystem, set())
                if base_name in popular:
                    return {
                        'similar_to': base_name,
                        'similarity': 0.85,
                        'package': package_name,
                        'ecosystem': ecosystem,
                        'detection_method': 'pattern_matching',
                        'pattern': pattern,
                    }
        
        return None


typosquatting_detector = TyposquattingDetector()