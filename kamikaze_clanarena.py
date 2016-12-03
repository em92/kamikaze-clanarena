import minqlx
from datetime import datetime
from time import sleep

SUPPORTED_GAMETYPES = ("ca")
KAMIKAZE_SPAWN_TIME = 10
SPAWN_POINTS = {
  "almostlost":     (-2239, -68, 342), # yellow armor/grenade launcher top
  "asylum":         (-224, -576, 408), # rocket launcher
  "bloodrun":       (-256, -320, 400), # grenade launcher
  "campgrounds":    (-576, -256, 18),  # mega/quad
  "eviscerated":    [ ( -1320, 480, -215), (936, 480, -216)],  # red armor and mega
  "hearth":         [ (-912, 1392, -16), (144, 2448, -16) ],   # plasma and shotgun
  "hiddenfortress": (-864, -384, 152), # railgun
  "longestyard":    [ (-576, -1088, 592), (-576, 1216, 592) ], # shotguns on different platforms
  "overkill":       (640, 224, 272),   # rocket launcher
  "quarantine":     (1536, 1120, 280), # lightning gun
  "": None
}

CS_ITEMS = 15

class kamikaze_clanarena(minqlx.Plugin):
  def __init__(self):
    self.add_hook("round_end",        self.handle_round_end)
    self.add_hook("round_start",      self.handle_round_start)
    self.add_hook("set_configstring", self.handle_set_configstring)
    # self.add_command("drop", self.cmd_drop_holdable)
    self.add_command("spawn_test",    self.spawn_kamikaze, 2)

    # reload config string
    # it runs handle_set_configstring
    minqlx.set_configstring(CS_ITEMS, minqlx.get_configstring(CS_ITEMS))

    self.enabled = False


  def cmd_drop_holdable(self, player, msg, channel):
    player.drop_holdable()
    return minqlx.RET_STOP_ALL


  def handle_round_end(self, data):
    self.enabled = False

    minqlx.destroy_kamikaze_timers()
    minqlx.remove_dropped_items()

    for player in self.players():
      player.holdable = None


  def handle_round_start(self, *args, **kwargs):
    if self.game.type_short not in SUPPORTED_GAMETYPES and self.game.map not in SPAWN_POINTS:
      self.enabled = False
      return

    self.enabled = True
    self.main_loop()


  def handle_set_configstring(self, index, value):
    if index != CS_ITEMS:
      return

    # forces client to load kamikaze models
    return value[0:37] + '1' + value[38:]


  def get_timestamp(self):
    return datetime.today().timestamp()


  def get_alive_players_from_team(self, team):
    return list( filter( lambda player: player.is_alive, self.teams()[team] ))


  def spawn_kamikaze(self, *args, **kwargs):
    for player in self.players():
      super().play_sound('sound/items/kamikazerespawn.wav', player)

    spawn_points = SPAWN_POINTS[ self.game.map ]

    if type(spawn_points) is tuple:
      spawn_points = [spawn_points]

    for spawn_point in spawn_points:
      minqlx.spawn_item(37, *spawn_point)


  @minqlx.thread
  def main_loop(self):
    round_start_time = self.get_timestamp()
    while self.enabled:
      if self.get_timestamp() - round_start_time > KAMIKAZE_SPAWN_TIME:
        self.spawn_kamikaze()
        break
      sleep(0.5)
