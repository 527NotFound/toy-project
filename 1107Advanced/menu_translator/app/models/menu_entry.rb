require 'active_storage'

class MenuEntry < ApplicationRecord
  has_one_attached :image
end