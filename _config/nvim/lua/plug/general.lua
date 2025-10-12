return {
  {
    "rhysd/git-messenger.vim",
    cmd = "GitMessenger",
    lazy = false,
    config = function()
      -- vim.g.git_messenger_no_default_mappings = true
      local u = require("core.utils")
      u.keymap("n", "<leader>gm", "<Cmd>GitMessenger<CR>", u.opts, "[GitMessenger] GitMessenger")
    end,
  },
  { "simeji/winresizer" },
  { "djoshea/vim-autoread" },
  { "tpope/vim-obsession" },
  { "mhinz/vim-startify" },
  {
    "okuuva/auto-save.nvim",
    version = "^1.0.0", -- see https://devhints.io/semver, alternatively use '*' to use the latest tagged release
    cmd = "ASToggle", -- optional for lazy loading on command
    event = { "InsertLeave", "TextChanged" }, -- optional for lazy loading on trigger events
    opts = {
      -- your config goes here
      -- or just leave it empty :)
    },
  },
  {
    "christoomey/vim-tmux-navigator",
    cmd = {
      "TmuxNavigateLeft",
      "TmuxNavigateDown",
      "TmuxNavigateUp",
      "TmuxNavigateRight",
      "TmuxNavigatePrevious",
    },
    keys = {
      { "<c-h>", "<cmd><C-U>TmuxNavigateLeft<cr>" },
      { "<c-j>", "<cmd><C-U>TmuxNavigateDown<cr>" },
      { "<c-k>", "<cmd><C-U>TmuxNavigateUp<cr>" },
      { "<c-l>", "<cmd><C-U>TmuxNavigateRight<cr>" },
      { "<c-\\>", "<cmd><C-U>TmuxNavigatePrevious<cr>" },
    },
  },
  {
    "folke/trouble.nvim",
    opts = {}, -- for default options, refer to the configuration section for custom setup.
    cmd = "Trouble",
    keys = {
      {
        "<leader>xx",
        "<cmd>Trouble diagnostics toggle<cr>",
        desc = "Diagnostics (Trouble)",
      },
      {
        "<leader>xX",
        "<cmd>Trouble diagnostics toggle filter.buf=0<cr>",
        desc = "Buffer Diagnostics (Trouble)",
      },
      {
        "<leader>cs",
        "<cmd>Trouble symbols toggle focus=false<cr>",
        desc = "Symbols (Trouble)",
      },
      {
        "<leader>cl",
        "<cmd>Trouble lsp toggle focus=false win.position=right<cr>",
        desc = "LSP Definitions / references / ... (Trouble)",
      },
      {
        "<leader>xL",
        "<cmd>Trouble loclist toggle<cr>",
        desc = "Location List (Trouble)",
      },
      {
        "<leader>xQ",
        "<cmd>Trouble qflist toggle<cr>",
        desc = "Quickfix List (Trouble)",
      },
    },
  },
  {
    "folke/flash.nvim",
    event = "VeryLazy",
    ---@type Flash.Config
    opts = {},
    -- stylua: ignore
    keys = {
      { "s", mode = { "n", "x", "o" }, function() require("flash").jump() end, desc = "Flash" },
      { "S", mode = { "n", "x", "o" }, function() require("flash").treesitter() end, desc = "Flash Treesitter" },
      { "r", mode = "o", function() require("flash").remote() end, desc = "Remote Flash" },
      { "R", mode = { "o", "x" }, function() require("flash").treesitter_search() end, desc = "Treesitter Search" },
      { "<c-s>", mode = { "c" }, function() require("flash").toggle() end, desc = "Toggle Flash Search" },
    },
  },
  { "nvim-neotest/nvim-nio" },
  { "nvim-lua/plenary.nvim", lazy = true },

  -- {
  --   "tibabit/vim-templates",
  --   config = function()
  --     local uv = vim.uv
  --     -- should override default paths rather than add
  --     vim.g.tmpl_search_paths = { vim.fn.stdpath("config") .. "templates" }
  --     local hostname = uv.os_gethostname()
  --     if vim.startswith(hostname, "hw") then
  --       vim.g.tmpl_author_name = vim.env.HW_NAME
  --       vim.g.tmpl_author_email = vim.env.EMAIL
  --     else
  --       vim.g.tmpl_author_email = vim.env.EMAIL
  --     end
  --   end,
  -- },

  {
    "MagicDuck/grug-far.nvim",
    keys = {
      {
        "<leader>gf",
        function()
          require("grug-far").open { transient = true, prefills = { search = vim.fn.expand("<cword>") } }
        end,
        mode = "n",
        desc = "[GrugFar] search <cword>",
      },
    },
    config = function()
      local grug_far = require("grug-far")
      grug_far.setup {
        startInInsertMode = false,
      }
      vim.api.nvim_create_autocmd("FileType", {
        group = vim.api.nvim_create_augroup("my-grug-far-custom-keybinds", { clear = true }),
        pattern = { "grug-far" },
        callback = function()
          vim.keymap.set("n", "<localleader>w", function()
            local state = unpack(grug_far.toggle_flags { "--fixed-strings" })
          end, { buffer = true, desc = "[GrugFar] Toggle fixed-strings" })
          vim.api.nvim_buf_set_keymap(
            0,
            "n",
            "<C-enter>",
            "<localleader>o<localleader>c",
            { desc = "[GrugFar] Open result and close GrugFar" }
          )
        end,
      })
    end,
  },

  -- profiling
  { "dstein64/vim-startuptime", cmd = "StartupTime" },

  -- chinese punctuation replacement
  {
    "hotoo/pangu.vim",
    cmd = { "Pangu", "PanguAll" },
    config = function()
      vim.g.pangu_rule_duplicate_punctuation = 0
      vim.g.pangu_rule_spacing = 0
      vim.g.pangu_rule_date = 0
      vim.g.pangu_punctuation_brackets = {}
      vim.g.pangu_punctuation_ellipsis = {}
    end,
  },

  {
    "MeanderingProgrammer/render-markdown.nvim",
    enabled = true,
    dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-tree/nvim-web-devicons" },
    ---@module 'render-markdown'
    ---@type render.md.UserConfig
    opts = {
      enabled = false,
      heading = {
        enabled = false,
      },
      paragraph = {
        enabled = false,
      },
      code = {
        enabled = true,
      },
      bullet = {
        enabled = false,
      },
      checkbox = {
        enabled = true,
      },
      quote = {
        enabled = true,
      },
    },
  },

  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    keys = {
      {
        "<leader>k",
        function()
          require("which-key").show { global = true, ["local"] = true }
        end,
        desc = "[wk] Buffer Local Keymaps",
      },
    },
    config = true,
    opts = {
      preset = "modern",
      expand = 20,
      show_help = false,
      show_keys = false,
      icons = {
        rules = false,
        colors = false,
      },
      sort = { "alphanum", "order", "group", "mod", "local" },
    },
  },

  {
    "moll/vim-bbye",
    keys = {
      { "<leader>qq", "<Cmd>Bdelete<CR>", desc = "[vim] delete buffer nicely" },
    },
  },

  { "kyazdani42/nvim-web-devicons", lazy = true },
  -- {
  --   "mortepau/codicons.nvim",
  --   config = true,
  -- },

  -- unix operation utilities(auto configured)
  { "tpope/vim-eunuch" },
}
