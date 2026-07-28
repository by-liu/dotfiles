-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

local function copy_file_path(relative)
  local path = vim.api.nvim_buf_get_name(0)

  if path == "" then
    vim.notify("Current buffer has no file path", vim.log.levels.WARN)
    return
  end

  if relative then
    path = vim.fn.fnamemodify(path, ":.")
  end

  vim.fn.setreg("+", path)
  vim.notify("Copied: " .. path)
end

vim.keymap.set("n", "<leader>zp", function()
  copy_file_path(true)
end, { desc = "Copy relative file path" })

vim.keymap.set("n", "<leader>zP", function()
  copy_file_path(false)
end, { desc = "Copy absolute file path" })
