from lumavate_signer import Signer
import sys
import os

public_key = os.environ.get('PUBLIC_KEY')
private_key = os.environ.get('PRIVATE_KEY')

s = Signer(public_key, private_key)
print(s.get_signed_url(sys.argv[1], sys.argv[2], sys.argv[3], None))
