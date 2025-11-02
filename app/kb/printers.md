# Printer Troubleshooting

**Symptom**: Printer not working after Windows update; error 0x00000bc4.

**Steps**
1. Reinstall or update the printer driver from the manufacturer site.
2. Restart the **Print Spooler** service: `services.msc` → *Print Spooler* → Restart.
3. Remove and re-add the printer; ensure correct port and driver mapping.
