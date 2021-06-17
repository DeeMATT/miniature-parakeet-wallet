
def validateKeys(payload, requiredKeys):
    # extract keys from payload
    payloadKeys = list(payload.keys())

    # check if extracted keys is present in requiredKeys
    missingKeys = [key for key in requiredKeys if key not in payloadKeys]
    return missingKeys
