import React from 'react'
import { cn } from '@/lib/utils'
import { Pencil, Trash2, GripVertical, ChevronRight, Plus } from 'lucide-react'
import { Switch } from '@/components/ui/switch'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

interface MenuCategoryItemProps {
  category: any
  isActive: boolean
  onClick: () => void
  onToggleStatus: (status: boolean) => void
  onEdit: () => void
  onDelete: () => void
  posManaged?: boolean
  /** Render as a sub-category (indented, no drag handle at root level) */
  isSubcategory?: boolean
  /** Show/hide the inline "add sub-category" button (only on parent rows) */
  onAddSubcategory?: () => void
  /** Sub-categories to render nested below this item */
  subcategories?: any[]
  /** Which sub-category (by name) is currently selected */
  activeSubcategoryId?: string | null
  onSubcategoryClick?: (cat: any) => void
  onSubcategoryEdit?: (cat: any) => void
  onSubcategoryDelete?: (cat: any) => void
  onSubcategoryToggleStatus?: (cat: any, status: boolean) => void
  /** Whether to render subcategories expanded */
  isExpanded?: boolean
  onToggleExpand?: () => void
}

export const MenuCategoryItem: React.FC<MenuCategoryItemProps> = ({
  category,
  isActive,
  onClick,
  onToggleStatus,
  onEdit,
  onDelete,
  posManaged = false,
  isSubcategory = false,
  onAddSubcategory,
  subcategories = [],
  activeSubcategoryId,
  onSubcategoryClick,
  onSubcategoryEdit,
  onSubcategoryDelete,
  onSubcategoryToggleStatus,
  isExpanded = true,
  onToggleExpand,
}) => {
  const hasSubcategories = subcategories.length > 0

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: category.name })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 100 : undefined,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div ref={setNodeRef} style={style}>
      {/* Main row */}
      <div
        className={cn(
          "group flex items-center gap-2 p-3 cursor-pointer rounded-lg transition-all border border-transparent",
          isSubcategory && "ml-5 pl-3 border-l-2 border-l-muted rounded-l-none",
          isActive
            ? "bg-accent text-accent-foreground shadow-md border-accent"
            : "hover:bg-muted text-muted-foreground hover:text-foreground"
        )}
        onClick={onClick}
      >
        {/* Drag handle — only on top-level categories */}
        {!posManaged && !isSubcategory && (
          <div {...attributes} {...listeners} className="flex items-center">
            <GripVertical className={cn(
              "h-4 w-4 shrink-0 opacity-80 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing",
              isActive && "opacity-100"
            )} />
          </div>
        )}

        {/* Expand/collapse chevron — only on parent categories that have subs */}
        {hasSubcategories && !isSubcategory && (
          <button
            onClick={(e) => { e.stopPropagation(); onToggleExpand?.() }}
            className="p-0.5 rounded hover:bg-background/30 transition-colors"
          >
            <ChevronRight className={cn(
              "h-3.5 w-3.5 transition-transform duration-200",
              isExpanded && "rotate-90"
            )} />
          </button>
        )}

        <div className="flex-1 min-w-0">
          <p className={cn(
            "text-sm font-medium truncate",
            isActive ? "text-accent-foreground" : "text-foreground",
            isSubcategory && "text-xs"
          )}>
            {category.display_name || category.category_name || category.name}
          </p>
          {category.item_count !== undefined && (
            <p className="text-[10px] opacity-70">
              {category.item_count} {category.item_count === 1 ? 'item' : 'items'}
            </p>
          )}
        </div>

        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          <Switch
            checked={category.is_active !== 0}
            onCheckedChange={onToggleStatus}
            className="scale-75"
          />
          {!posManaged && (
            <>
              {/* Add sub-category button — only on top-level non-sub rows */}
              {!isSubcategory && onAddSubcategory && (
                <button
                  onClick={onAddSubcategory}
                  title="Add sub-category"
                  className="p-1 rounded-md hover:bg-background/20 transition-colors text-muted-foreground hover:text-orange-500"
                >
                  <Plus className="h-3.5 w-3.5" />
                </button>
              )}
              <button
                onClick={onEdit}
                className="p-1 rounded-md hover:bg-background/20 dark:hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
              >
                <Pencil className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={onDelete}
                className="p-1 rounded-md hover:bg-destructive/20 text-destructive/70 hover:text-destructive transition-colors"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Sub-categories */}
      {hasSubcategories && isExpanded && (
        <div className="mt-0.5 space-y-0.5 ml-4 pl-3 border-l-2 border-l-primary/30">
          {subcategories.map((sub: any) => (
            <div
              key={sub.name}
              className={cn(
                "group flex items-center gap-2 px-2.5 py-1.5 cursor-pointer rounded-md transition-all",
                activeSubcategoryId === sub.name
                  ? "bg-primary/15 text-primary border border-primary/30"
                  : "hover:bg-muted/60 text-muted-foreground hover:text-foreground border border-transparent"
              )}
              onClick={() => onSubcategoryClick?.(sub)}
            >
              {/* Sub-indicator dot */}
              <span className={cn(
                "w-1.5 h-1.5 rounded-full shrink-0",
                activeSubcategoryId === sub.name ? "bg-primary" : "bg-muted-foreground/40 group-hover:bg-muted-foreground/70"
              )} />
              <div className="flex-1 min-w-0">
                <p className={cn(
                  "text-xs font-medium truncate",
                  activeSubcategoryId === sub.name ? "text-primary" : "text-foreground/80"
                )}>
                  {sub.display_name || sub.category_name || sub.name}
                </p>
              </div>
              <div className={cn(
                "flex items-center gap-1 transition-opacity",
                activeSubcategoryId === sub.name ? "opacity-100" : "opacity-0 group-hover:opacity-100"
              )} onClick={(e) => e.stopPropagation()}>
                <Switch
                  checked={sub.is_active !== 0}
                  onCheckedChange={(status) => onSubcategoryToggleStatus?.(sub, status)}
                  className="scale-[0.65]"
                />
                {!posManaged && (
                  <>
                    <button
                      onClick={() => onSubcategoryEdit?.(sub)}
                      className="p-1 rounded hover:bg-background/30 transition-colors text-muted-foreground hover:text-foreground"
                    >
                      <Pencil className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => onSubcategoryDelete?.(sub)}
                      className="p-1 rounded hover:bg-destructive/20 text-destructive/60 hover:text-destructive transition-colors"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
