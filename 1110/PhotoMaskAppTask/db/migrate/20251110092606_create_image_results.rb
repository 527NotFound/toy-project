class CreateImageResults < ActiveRecord::Migration[7.1]
  def change
    create_table :image_results do |t|
      t.string :original_filename
      t.string :processed_image_path
      t.integer :status
      t.text :description

      t.timestamps
    end
  end
end
