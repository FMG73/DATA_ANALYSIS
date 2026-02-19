IF 
    SUM(
        IF [Estado 90 Días] = "Mayor 90 días" THEN 1 ELSE 0 END
    )
    /
    COUNT([Estado 90 Días])
    > 0.01
THEN 0
ELSE 1
END