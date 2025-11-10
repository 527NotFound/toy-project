class CreateMenuEntries < ActiveRecord::Migration[7.1]
  def change
    create_table :menu_entries do |t|
      t.text :original_text
      t.text :translated_text

      t.timestamps
    end
  end
end
