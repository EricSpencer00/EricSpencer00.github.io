document.addEventListener('DOMContentLoaded', function() {
  // Get all filter tags
  const filterTags = document.querySelectorAll('.filter-tag');
  // Get all project cards
  const projectCards = document.querySelectorAll('.project-card');
  // Get no results message
  const noResults = document.querySelector('.no-results');
  // Get filter tags container
  const filterTagsContainer = document.querySelector('.filter-tags');
  
  // Initialize active filters
  let activeFilters = [];
  
  // Add click event to filter tags
  filterTags.forEach(tag => {
    tag.addEventListener('click', function() {
      const filter = this.getAttribute('data-tag');
      
      // Toggle active class
      this.classList.toggle('active');
      
      // Update active filters
      if (this.classList.contains('active')) {
        // Add filter
        activeFilters.push(filter);
      } else {
        // Remove filter
        activeFilters = activeFilters.filter(f => f !== filter);
      }
      
      // Apply filters
      filterProjects(activeFilters);
    });
  });
  
  // Toggle filter tags display
  const toggleFiltersBtn = document.querySelector('.toggle-filters-btn');
  if (toggleFiltersBtn && filterTagsContainer) {
    toggleFiltersBtn.addEventListener('click', function() {
      filterTagsContainer.classList.toggle('expanded');
      this.textContent = filterTagsContainer.classList.contains('expanded') ? 'Show Less' : 'Show All Filters';
    });
  }
  
  // Show all projects button
  const showAllBtn = document.querySelector('.show-all-btn');
  if (showAllBtn) {
    showAllBtn.addEventListener('click', function() {
      // Reset all filters
      filterTags.forEach(tag => tag.classList.remove('active'));
      activeFilters = [];
      filterProjects(activeFilters);
    });
  }
  
  // Filter projects based on active filters
  function filterProjects(filters) {
    let visibleCount = 0;
    
    // If no filters active, show all projects
    if (filters.length === 0) {
      projectCards.forEach(card => {
        card.classList.remove('hidden');
        visibleCount++;
      });
    } else {
      // Filter projects based on active filters
      projectCards.forEach(card => {
        const cardTags = card.getAttribute('data-tags').split(',');
        const isVisible = filters.some(filter => cardTags.includes(filter));
        
        if (isVisible) {
          card.classList.remove('hidden');
          visibleCount++;
        } else {
          card.classList.add('hidden');
        }
      });
    }
    
    // Show/hide no results message
    if (noResults) {
      if (visibleCount === 0) {
        noResults.style.display = 'block';
      } else {
        noResults.style.display = 'none';
      }
    }
  }
});
