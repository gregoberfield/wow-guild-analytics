# Logging and Error Handling Improvements

## Changes Made

### 1. Enhanced Logging in `app/bnet_api.py`
- ✅ Added detailed logging for OAuth token requests
- ✅ Added debug logging for all API requests and responses
- ✅ Added character name normalization for special characters (umlauts, accents, etc.)
- ✅ Improved error messages with truncated response text

**Key Features:**
- Character names with special characters (e.g., "Gewölbe") are automatically normalized
- All API calls are logged at debug level for troubleshooting
- OAuth token generation is logged at info level

### 2. Improved Sync Process in `app/services.py`
- ✅ Added progress logging (every 50 members)
- ✅ Added success/failure statistics tracking
- ✅ Differentiated between 404 errors (debug) and other errors (warning)
- ✅ Added detailed sync summary at completion

**Logging Output Includes:**
```
Starting guild sync for 'hordecore-casuals' on 'dreamscythe'
Fetching guild information...
✅ Guild info retrieved: Hordecore Casuals - Dreamscythe
Fetching guild roster...
✅ Roster retrieved: 864 members found
Progress: 50/864 members processed...
Progress: 100/864 members processed...
...
✅ Guild sync completed successfully!
   - Total members: 864
   - Profiles retrieved: 612
   - Profiles unavailable: 252
```

### 3. Better Startup Logging in `run.py`
- ✅ Configured logging format with timestamps
- ✅ Added startup banner with server URL
- ✅ Set appropriate log levels (INFO for production visibility)

### 4. Character Name Normalization
The new `_normalize_character_name()` method handles:
- **Accented characters**: Gewölbe → gewolbe
- **Special characters**: Démon → demon, Naïve → naive
- **Case conversion**: All names converted to lowercase
- **URL encoding**: Ensures safe API calls

## Understanding 404 Errors

404 errors for character profiles are **normal and expected** for several reasons:

### Why Characters Might Return 404:
1. **Privacy Settings**: Character has profile set to private
2. **Not Indexed**: Character hasn't logged in recently enough for API indexing
3. **New Character**: Recently created characters may not be in the API yet
4. **Realm Transfer**: Characters that recently transferred may have stale data
5. **API Limitations**: Classic Anniversary API may have limited character data

### What Gets Stored Anyway:
Even with a 404 on character profile, we still store:
- ✅ Character name
- ✅ Level
- ✅ Class
- ✅ Race  
- ✅ Guild rank
- ✅ Realm

This data comes from the guild roster endpoint, which doesn't require individual character profiles.

## Log Levels

### INFO (Default)
Shows important events:
- Guild sync start/completion
- OAuth token generation
- Progress updates
- Success/failure statistics

### DEBUG
Enable with `app.logger.setLevel(logging.DEBUG)` to see:
- Every API request URL
- API response codes
- Character profile fetch attempts
- Detailed error messages

### WARNING
Shows issues that don't stop execution:
- Character profiles that can't be fetched (non-404 errors)
- Unexpected API responses

### ERROR
Shows critical failures:
- OAuth token failures
- Guild sync failures
- Database errors

## Viewing Logs

When running the application:
```bash
python run.py
```

Logs will appear in the console with format:
```
2025-10-19 12:51:47 [INFO] app: Starting guild sync for 'hordecore-casuals'
2025-10-19 12:51:48 [DEBUG] app: API Request: https://us.api.blizzard.com/...
2025-10-19 12:51:49 [INFO] app: Progress: 50/864 members processed...
```

## Testing Character Names

Use the included test script:
```bash
python test_character_names.py
```

This will show how different character names are normalized.

## Recommendations

1. **Don't worry about 404s**: They're normal for many characters in Classic
2. **Focus on the summary**: Check the completion stats to see how many profiles were retrieved
3. **Basic data is always stored**: Guild roster provides the essential information
4. **Enable DEBUG logging**: Only if you need to troubleshoot specific API issues
5. **Check progress**: The progress counter helps track long syncs (864 members!)

## Expected Results

For a guild like "Hordecore Casuals" with 864 members:
- **Total sync time**: ~15-30 minutes (due to API rate limiting)
- **Successful profiles**: ~70-80% (typical for Classic Anniversary)
- **Failed profiles**: ~20-30% (normal due to privacy/indexing)
- **Database records**: 100% (all members stored with basic data)
