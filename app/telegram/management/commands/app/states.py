from aiogram.fsm.state import StatesGroup, State

class TrackState(StatesGroup):
    waiting_for_track = State()

class CourierOrderStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()