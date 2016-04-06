# auth_ldaps

This module provides for the LDAPS protocol. It allows you to selected between LDAP and LDAPS.

This may be needed to make LDAP work with Windows Active Directory.

It also changes a check for ==1 to >=1, as testing showed more than 1 result was returned. 
