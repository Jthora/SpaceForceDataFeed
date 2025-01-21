import streamlit as st
from utils.db import get_db_connection
import logging
from typing import List, Dict, Any, Optional

def get_all_categories() -> List[Dict[str, Any]]:
    """Get all categories from the database"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name FROM categories ORDER BY name")
                return cur.fetchall() or []
    except Exception as e:
        logging.error(f"Error fetching categories: {str(e)}")
        return []

def add_category(name: str) -> None:
    """Add a new category"""
    if not name:
        st.warning("Category name cannot be empty")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id",
                    (name,)
                )
                conn.commit()
                result = cur.fetchone()
                if result:
                    st.success(f"Category '{name}' added successfully!")
                else:
                    st.warning(f"Category '{name}' already exists.")
    except Exception as e:
        logging.error(f"Error adding category: {str(e)}")
        st.error(f"Error adding category: {str(e)}")

def edit_category(old_name: str, new_name: str) -> None:
    """Edit category name"""
    if not old_name or not new_name:
        st.warning("Category names cannot be empty")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE categories SET name = %s WHERE name = %s",
                    (new_name, old_name)
                )
                conn.commit()
                if cur.rowcount > 0:
                    st.success(f"Category renamed from '{old_name}' to '{new_name}'")
                else:
                    st.warning("Category not found")
    except Exception as e:
        logging.error(f"Error editing category: {str(e)}")
        st.error(f"Error editing category: {str(e)}")

def delete_category(name: str) -> None:
    """Delete a category"""
    if not name:
        st.warning("Category name cannot be empty")
        return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # First, update any items using this category to 'Uncategorized'
                cur.execute(
                    """
                    WITH uncategorized AS (
                        SELECT id FROM categories WHERE name = 'Uncategorized'
                        LIMIT 1
                    )
                    UPDATE news 
                    SET category_id = (SELECT id FROM uncategorized)
                    WHERE category_id = (
                        SELECT id FROM categories WHERE name = %s
                    )
                    """,
                    (name,)
                )

                # Then delete the category
                cur.execute(
                    "DELETE FROM categories WHERE name = %s AND name != 'Uncategorized'",
                    (name,)
                )
                conn.commit()
                if cur.rowcount > 0:
                    st.success(f"Category '{name}' deleted successfully")
                else:
                    st.warning("Category not found or cannot be deleted")
    except Exception as e:
        logging.error(f"Error deleting category: {str(e)}")
        st.error(f"Error deleting category: {str(e)}")

def render_category_manager() -> None:
    """Render category management UI in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Category Management")

    # Get existing categories
    categories = [cat.get('name', '') for cat in get_all_categories() if cat]

    # Add new category
    new_category = st.sidebar.text_input("Add New Category")
    if st.sidebar.button("Add Category") and new_category:
        add_category(new_category)
        st.rerun()

    # Edit/Delete existing categories
    if categories:
        st.sidebar.markdown("### Manage Existing Categories")
        selected_category = st.sidebar.selectbox(
            "Select Category",
            categories,
            key="category_manager"
        )

        if selected_category:
            col1, col2 = st.sidebar.columns(2)

            # Edit category
            with col1:
                if st.button("Edit"):
                    new_name = st.text_input("New name", value=selected_category)
                    if st.button("Save") and new_name != selected_category:
                        edit_category(selected_category, new_name)
                        st.rerun()

            # Delete category
            with col2:
                if selected_category != "Uncategorized" and st.button("Delete"):
                    if st.sidebar.checkbox("Confirm deletion?"):
                        delete_category(selected_category)
                        st.rerun()