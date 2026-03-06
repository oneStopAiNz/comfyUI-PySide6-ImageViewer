from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt

class WorkflowInspector(QWidget):
    """
    Shows a combo box of all parsed ComfyUI nodes.
    Shows a table of inputs for the currently selected node.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Combo Box for selecting nodes
        self.node_combo = QComboBox()
        self.layout.addWidget(self.node_combo)
        
        self.node_combo.currentIndexChanged.connect(self.on_node_selected)

        # Table for displaying parameters
        self.param_table = QTableWidget()
        self.param_table.setColumnCount(2)
        self.param_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        
        # Stretch value column to fill remaining space
        header = self.param_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.param_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.param_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.param_table)

        # State mapping node strings to actual dict structures
        self.current_workflow_data = {}

    def load_workflow(self, parsed_nodes):
        """
        Loads the provided parsed complete workflow dictionary.
        Updates the ComboBox and clears/repopulates the Table.
        """
        self.node_combo.clear()
        self.param_table.setRowCount(0)
        self.current_workflow_data = parsed_nodes or {}

        if not self.current_workflow_data:
            return

        # Populate the combo box
        for node_id, node_info in self.current_workflow_data.items():
            # Format: "node_id: Node_Title" (e.g. "4: KSampler" or "4: Primary Sampler")
            node_title = node_info.get("title", node_info.get("type", "Unknown"))
            display_text = f"{node_id}: {node_title}"
            
            # Add to combobox and store the node_id string in the invisible UserData
            self.node_combo.addItem(display_text, userData=node_id)
            
        # Default sort node ids as integers if possible
        self._sort_combo_items()
            
    def _sort_combo_items(self):
         # Extract items, try to sort by integer node ID, re-insert
         items = []
         for i in range(self.node_combo.count()):
             text = self.node_combo.itemText(i)
             data = self.node_combo.itemData(i)
             items.append((text, data))
             
         try:
             # Sort by integer node_id
             items.sort(key=lambda x: int(x[1]))
         except ValueError:
             # Fallback string sort if node IDs aren't integers
             items.sort(key=lambda x: x[1])
             
         self.node_combo.blockSignals(True)
         self.node_combo.clear()
         for text, data in items:
             self.node_combo.addItem(text, userData=data)
         self.node_combo.blockSignals(False)
         
         # Force update of first node
         if self.node_combo.count() > 0:
             self.node_combo.setCurrentIndex(0)
             self.on_node_selected(0)

    def on_node_selected(self, index):
        """Displays the parameters of the selected node."""
        if index < 0 or index >= self.node_combo.count():
            return

        # Retrieve the hidden node_id we stored
        node_id = self.node_combo.itemData(index)
        
        node_data = self.current_workflow_data.get(node_id, {})
        inputs = node_data.get("inputs", {})
        
        self.param_table.setRowCount(len(inputs))
        
        row = 0
        for key, value in sorted(inputs.items()):
            # Create Table Items
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(value))
            
            # Place in table
            self.param_table.setItem(row, 0, key_item)
            self.param_table.setItem(row, 1, value_item)
            
            row += 1

    def highlight_parameters(self, changed_keys):
        """
        Highlights changed parameters in yellow based on a list of keys.
        (Task 9 feature)
        """
        # Iterate over currently displayed rows
        for row in range(self.param_table.rowCount()):
            key_item = self.param_table.item(row, 0)
            value_item = self.param_table.item(row, 1)
            
            if not key_item or not value_item:
                continue
                
            if key_item.text() in changed_keys:
                # Highlight in theme orange
                orange = QColor("#d35400")
                white = QColor("#ffffff")
                
                key_item.setBackground(orange)
                key_item.setForeground(white)
                key_item.setFont(QFont("Arial", weight=QFont.Bold))
                
                value_item.setBackground(orange)
                value_item.setForeground(white)
                value_item.setFont(QFont("Arial", weight=QFont.Bold))
            else:
                # Reset to default (let QSS handle the default look)
                key_item.setData(Qt.BackgroundRole, None)
                key_item.setData(Qt.ForegroundRole, None)
                key_item.setFont(QFont())
                
                value_item.setData(Qt.BackgroundRole, None)
                value_item.setData(Qt.ForegroundRole, None)
                value_item.setFont(QFont())
    
    def get_current_node_id(self):
        """Returns the node_id currently selected in the combo box."""
        idx = self.node_combo.currentIndex()
        if idx >= 0:
            return self.node_combo.itemData(idx)
        return None
