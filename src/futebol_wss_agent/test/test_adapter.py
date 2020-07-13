from futebol_wss_agent.lib.finisar_serial_adapter import Adapter
from futebol_wss_agent.lib.grid import FixedGrid
from futebol_wss_agent.lib.wss import Wss

adapter = Adapter()
f0 = FixedGrid.DEFAULT_FIRST_FREQUENCY - 6.25e-3
grid = FixedGrid(bandwidth=50.0, spacing=0.0, first_frequency=f0)
wss = Wss(grid, adapter)
#grid_left = wss.grid['frequency', :194.65]
wss.grid[0:7].port = 1

#grid_right = wss.grid['frequency', 194.65:]
grid_right = wss.grid[8:15]
grid_right.port = 3
grid_right.attenuation = 5
print("Configuration FixedGrid")
print(wss.commit())
