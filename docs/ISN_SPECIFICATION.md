# ISN — Internet Subscriber Number Specification

The **Internet Subscriber Number (ISN)** is the global addressing standard used by the ICC library for Internet communications (VOIP, blockchain integration, etc.).

## 1. Format

The ISN consists of 15 digits, typically formatted with hyphens for readability:

```
ICC-RRRR-SSSS-SSSS
```

### Components

1. **ICC (3 digits)**
   - **Internet Calling Code**: Represents the destination network.
   - Can be a **Country Code** (e.g., `100` for Russia).
   - Can be a **Special Code** (e.g., `111` for Educational Institutions).
   - Can be an **App Code** (e.g., `010` for Mobyap Internal Channel 1).

2. **RRRR (4 digits)**
   - **Region and Purpose Code**: Used for internal routing within the ICC network.
   - Allows up to 10,000 unique regions or purposes per ICC code.
   - Default/fallback value is often `0001`.

3. **SSSS-SSSS (8 digits)**
   - **Subscriber Number**: The unique identifier for the end user or service.
   - Allows up to 100 million unique subscribers per Region Code.

## 2. Examples

**Country ISN (Assigned by Land Area):**
`100-1234-5678-0321`
- `100` = Russia
- `1234` = Region/Routing Code
- `56780321` = Subscriber Number

**Special Code ISN (Global Services):**
`333-0000-0000-0911`
- `333` = Emergency Services
- `0000` = Global Routing
- `00000911` = Subscriber/Service Number

**App Code ISN (Mobyap Channels):**
`010-0001-9999-8888`
- `010` = Mobyap Channel 1
- `0001` = Routing
- `99998888` = Subscriber

## 3. Data Representation

### Raw Digits
When transmitted in protocols that do not support hyphens, the ISN is represented as a contiguous 15-digit string:
`100123456780321`

### Integers vs. Strings
Because ISNs (and their components) can start with zeroes (e.g., App Codes like `010`, or region codes like `0001`), the full ISN, region code, and subscriber number **must** be stored and transmitted as strings to prevent truncation.

The ICC code itself is typically parsed as an integer (`10`, `100`, etc.) internally but zero-padded to 3 digits (`010`, `100`) when formatted as a string.

## 4. Validation Rules

A valid ISN must strictly adhere to the following:
1. Must contain exactly 15 numeric digits (ignoring hyphens/spaces).
2. The first 3 digits must form a recognized ICC code (either a country code `100–999`, a special code `111–909`, or an app code `010–090`).
3. App codes must always start with `0` and end with `0`.
4. Country/Special codes must never start with `0`.
