from aiogram.fsm.state import StatesGroup, State

class TrackState(StatesGroup):
    waiting_for_track = State()