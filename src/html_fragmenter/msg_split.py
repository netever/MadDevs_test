from typing import Generator, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from copy import copy
from .exceptions import FragmentationError

MAX_LEN = 4096

class HTMLSplitter:
    """
    Класс для разделения HTML-контента на фрагменты заданной максимальной длины.
    Используется для обработки больших HTML-документов, которые нужно разбить
    на меньшие части с сохранением валидной структуры HTML.
    """
    
    def __init__(self, max_len=MAX_LEN):
        """
        Инициализация сплиттера.
        
        Args:
            max_len: Максимальная длина каждого фрагмента в символах
        """
        self.max_len = max_len
        
    def _copy_tag_with_attrs(self, tag: Tag) -> Tag:
        """
        Создает полную копию тега со всеми его атрибутами.
        
        Args:
            tag: Исходный HTML-тег
            
        Returns:
            Новый тег с скопированными атрибутами
        """
        return Tag(None, tag.name, attrs=dict(tag.attrs))
        
    def _get_parent_tags(self, element: Tag) -> List[Tag]:
        """
        Возвращает список родительских тегов от корня до указанного элемента.
        
        Args:
            element: HTML-элемент, для которого нужно найти родителей
            
        Returns:
            Список тегов в порядке от корня документа до родителя элемента
        """
        parents = []
        parent = element.parent
        while parent and isinstance(parent, Tag):
            parents.append(parent)
            parent = parent.parent
        return parents[::-1]
    
    def _estimate_length(self, soup: BeautifulSoup) -> int:
        """
        Оценивает длину HTML-вывода, включая теги.
        
        Args:
            soup: BeautifulSoup объект для оценки
            
        Returns:
            Примерная длина HTML в символах
        """
        return len(str(soup))
    
    def _find_split_point(self, element: Tag, current_length: int) -> Optional[Tag]:
        """
        Находит подходящую точку для разделения контента внутри элемента.
        
        Args:
            element: HTML-элемент для поиска точки разделения
            current_length: Текущая накопленная длина
            
        Returns:
            Тег, перед которым нужно сделать разделение, или None если точка не найдена
        """
        if not isinstance(element, Tag):
            return None
            
        # Пробуем разделить по прямым потомкам
        for child in element.children:
            if isinstance(child, Tag):
                child_length = len(str(child))
                if current_length + child_length > self.max_len:
                    return child
                current_length += child_length
                
        return None
    
    def _can_be_split(self, element: Tag) -> bool:
        """
        Проверяет, можно ли разделить элемент на меньшие части.
        
        Args:
            element: HTML-элемент для проверки
            
        Returns:
            True если элемент можно разделить, False в противном случае
        """
        # Текстовые узлы нельзя разделить
        if isinstance(element, NavigableString):
            return False
            
        # Элементы без потомков нельзя разделить
        if not element.contents:
            return False
            
        # Проверяем, есть ли среди прямых потомков блочные элементы
        return any(isinstance(child, Tag) for child in element.children)
    
    def _create_fragment(self, elements: List[Tag], parent_tags: List[Tag] = None) -> BeautifulSoup:
        """
        Создает новый HTML-фрагмент с правильной иерархией тегов.
        
        Args:
            elements: Список элементов для включения во фрагмент
            parent_tags: Список родительских тегов (опционально)
            
        Returns:
            BeautifulSoup объект с созданным фрагментом
        """
        fragment = BeautifulSoup('', 'html.parser')
        current = fragment
        
        # Добавляем иерархию родителей, если она предоставлена
        if parent_tags:
            for parent in parent_tags:
                new_parent = self._copy_tag_with_attrs(parent)
                current.append(new_parent)
                current = new_parent
        
        # Добавляем элементы
        for elem in elements:
            if isinstance(elem, Tag):
                new_elem = copy(elem)
                current.append(new_elem)
            else:
                current.append(str(elem))
                
        return fragment

    def split_message(self, source: str) -> Generator[str, None, None]:
        """
        Основной метод для разделения HTML на фрагменты.
        
        Args:
            source: Исходный HTML-текст для разделения
            
        Yields:
            Последовательность строк, каждая из которых представляет собой
            валидный HTML-фрагмент не превышающий максимальную длину
            
        Raises:
            FragmentationError: Если невозможно разделить контент по заданным правилам
        """
        if not source.strip():
            return
            
        soup = BeautifulSoup(source, 'html.parser')
        current_elements = []
        current_length = 0
        
        for element in soup.children:
            if isinstance(element, NavigableString) and not element.strip():
                continue
                
            element_length = len(str(element))
            
            # Проверяем, не слишком ли велик сам элемент
            if element_length > self.max_len:
                # Если нельзя разделить, вызываем ошибку
                if not self._can_be_split(element):
                    raise FragmentationError(f"Element of length {element_length} cannot be split")
                    
                # Пробуем разделить в подходящей точке
                split_point = self._find_split_point(element, 0)
                if not split_point:
                    raise FragmentationError("Cannot find suitable split point")
                    
                # Обрабатываем первую часть
                first_part = BeautifulSoup('', 'html.parser')
                current = first_part
                for child in element.children:
                    if child is split_point:
                        break
                    current.append(copy(child))
                
                if self._estimate_length(first_part) <= self.max_len:
                    yield str(first_part)
                else:
                    raise FragmentationError("First part exceeds maximum length")
                    
                # Рекурсивно обрабатываем оставшиеся части
                remaining = BeautifulSoup('', 'html.parser')
                for child in split_point.next_siblings:
                    remaining.append(copy(child))
                    
                yield from self.split_message(str(remaining))
                
            # Если добавление этого элемента превысит максимальную длину
            elif current_length + element_length > self.max_len:
                # Выдаем текущий фрагмент, если он не пустой
                if current_elements:
                    fragment = self._create_fragment(current_elements)
                    yield str(fragment)
                    
                # Начинаем новый фрагмент с текущим элементом
                current_elements = [element]
                current_length = element_length
                
            else:
                # Добавляем элемент к текущему фрагменту
                current_elements.append(element)
                current_length += element_length
        
        # Выдаем последний фрагмент, если он не пустой
        if current_elements:
            fragment = self._create_fragment(current_elements)
            if str(fragment).strip():
                yield str(fragment)

def split_message(source: str, max_len=MAX_LEN) -> Generator[str, None, None]:
    """
    Вспомогательная функция для разделения сообщений.
    
    Args:
        source: Исходный HTML для разделения
        max_len: Максимальная длина каждого фрагмента
        
    Returns:
        Генератор строк HTML-фрагментов
    """
    splitter = HTMLSplitter(max_len=max_len)
    yield from splitter.split_message(source)