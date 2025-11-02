# VPN Connection Issues

**Symptom**: Users cannot connect to VPN; authentication or DNS errors.

**Steps**
1. Check user group membership and VPN profile assignment.
2. Reset DNS cache: `ipconfig /flushdns` (Windows) or `dscacheutil -flushcache` (macOS).
3. Rotate credentials and verify MFA enrollment.
