import { useState, useEffect } from 'react'
import menuApi from '../../api/menuApi'
import adminApi from '../../api/adminApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Modal from '../../components/common/Modal'
import Badge from '../../components/common/Badge'
import { formatPrice } from '../../utils/formatters'
import toast from 'react-hot-toast'

const DEFAULT_FORM = {
	item_name: '',
	category: 'Snacks',
	price: '',
	prep_time_estimate: '',
	complexity_score: 1,
	is_available: true,
	unavailable_reason: '',
	image_url: null,
}

const getErrorMessage = (error, fallback) => {
	const detail = error?.response?.data?.detail
	if (typeof detail === 'string') return detail
	if (Array.isArray(detail)) {
		const first = detail[0]
		if (first?.msg) return first.msg
		return fallback
	}
	if (detail && typeof detail === 'object') {
		if (typeof detail.message === 'string') return detail.message
		return fallback
	}
	if (typeof error?.message === 'string') return error.message
	return fallback
}

export default function MenuManagementPage() {
	const [menu, setMenu] = useState(null)
	const [loading, setLoading] = useState(true)
	const [showAddModal, setShowAddModal] = useState(false)
	const [showEditModal, setShowEditModal] = useState(false)
	const [selectedImage, setSelectedImage] = useState(null)
	const [selectedEditImage, setSelectedEditImage] = useState(null)
	const [editingItemId, setEditingItemId] = useState(null)
	const [adding, setAdding] = useState(false)
	const [editing, setEditing] = useState(false)
	const [formData, setFormData] = useState(DEFAULT_FORM)
	const [editFormData, setEditFormData] = useState(DEFAULT_FORM)

	useEffect(() => { fetchMenu() }, [])

	const fetchMenu = async () => {
		try {
			const data = await menuApi.getFullMenu()
			setMenu(data)
		} catch (error) {
			console.error(error)
		} finally {
			setLoading(false)
		}
	}

	const handleAdd = async () => {
		if (!formData.item_name || !formData.price || !formData.prep_time_estimate) {
			toast.error('Name, price and prep time are required')
			return
		}

		setAdding(true)
		try {
			let imageUrl = null
			if (selectedImage) {
				const upload = await adminApi.uploadMenuImage(selectedImage)
				imageUrl = upload.image_url
			}

			await adminApi.addMenuItem({
				...formData,
				price: parseFloat(formData.price),
				prep_time_estimate: parseInt(formData.prep_time_estimate),
				complexity_score: parseInt(formData.complexity_score),
				is_available: formData.is_available,
				unavailable_reason: formData.is_available ? null : (formData.unavailable_reason || 'Out of stock'),
				image_url: imageUrl
			})
			toast.success('Item added!')
			setShowAddModal(false)
			setFormData(DEFAULT_FORM)
			setSelectedImage(null)
			fetchMenu()
		} catch (error) {
			const message = getErrorMessage(error, 'Failed to add item')
			toast.error(message)
		} finally {
			setAdding(false)
		}
	}

	const openEditModal = (item) => {
		setEditingItemId(item.item_id)
		setEditFormData({
			item_name: item.item_name || '',
			category: item.category || 'Snacks',
			price: item.price ?? '',
			prep_time_estimate: item.prep_time_estimate ?? '',
			complexity_score: item.complexity_score ?? 1,
			is_available: item.is_available,
			unavailable_reason: item.unavailable_reason || '',
			image_url: item.image_url || null,
		})
		setSelectedEditImage(null)
		setShowEditModal(true)
	}

	const handleEdit = async () => {
		if (!editFormData.item_name || !editFormData.price || !editFormData.prep_time_estimate) {
			toast.error('Name, price and prep time are required')
			return
		}

		setEditing(true)
		try {
			let imageUrl = editFormData.image_url
			if (selectedEditImage) {
				const upload = await adminApi.uploadMenuImage(selectedEditImage)
				imageUrl = upload.image_url
			}

			await adminApi.updateMenuItem(editingItemId, {
				item_name: editFormData.item_name,
				category: editFormData.category,
				price: parseFloat(editFormData.price),
				prep_time_estimate: parseInt(editFormData.prep_time_estimate),
				complexity_score: parseInt(editFormData.complexity_score),
				is_available: editFormData.is_available,
				unavailable_reason: editFormData.is_available ? null : (editFormData.unavailable_reason || 'Out of stock'),
				image_url: imageUrl,
			})

			toast.success('Item updated!')
			setShowEditModal(false)
			setSelectedEditImage(null)
			setEditingItemId(null)
			fetchMenu()
		} catch (error) {
			const message = getErrorMessage(error, 'Failed to update item')
			toast.error(message)
		} finally {
			setEditing(false)
		}
	}

	const handleDelete = async (itemId, name) => {
		if (!confirm(`Delete "${name}"?`)) return
		try {
			await adminApi.deleteMenuItem(itemId)
			toast.success(`${name} deleted`)
			fetchMenu()
		} catch (error) {
			toast.error('Failed to delete')
		}
	}

	if (loading) return <LoadingSpinner size="lg" />

	const allItems = menu?.categories?.flatMap(c => c.items) || []

	return (
		<div className="page-container">
			<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
				<h1 className="page-title mb-0">Menu Management</h1>
				<button onClick={() => setShowAddModal(true)} className="btn-primary w-full sm:w-auto">+ Add Item</button>
			</div>

			{/* Mobile Cards */}
			<div className="space-y-3 sm:hidden">
				{allItems.length === 0 ? (
					<div className="card text-center text-sm text-gray-500">No menu items found.</div>
				) : allItems.map(item => (
					<div key={item.item_id} className="card">
						<div className="flex items-start justify-between gap-3">
							<div>
								<p className="font-semibold text-gray-900">{item.item_name}</p>
								<p className="text-xs text-gray-500">{item.category}</p>
							</div>
							<Badge
								text={item.is_available ? 'Available' : 'Unavailable'}
								variant={item.is_available ? 'success' : 'danger'}
							/>
						</div>

						<div className="mt-3 flex items-center justify-between text-sm text-gray-600">
							<span>{formatPrice(item.price)}</span>
							<span>{item.prep_time_estimate} min</span>
						</div>

						<div className="mt-3 grid grid-cols-2 gap-2">
							<button
								onClick={() => openEditModal(item)}
								className="py-2 rounded-lg text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100"
							>
								Edit
							</button>
							<button
								onClick={() => handleDelete(item.item_id, item.item_name)}
								className="py-2 rounded-lg text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100"
							>
								Delete
							</button>
						</div>
					</div>
				))}
			</div>

			{/* Desktop Table */}
			<div className="card table-scroll hidden sm:block">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b border-gray-200 text-left text-gray-500">
							<th className="pb-3 font-medium">Name</th>
							<th className="pb-3 font-medium">Category</th>
							<th className="pb-3 font-medium">Price</th>
							<th className="pb-3 font-medium">Prep Time</th>
							<th className="pb-3 font-medium">Status</th>
							<th className="pb-3 font-medium">Actions</th>
						</tr>
					</thead>
					<tbody>
						{allItems.map(item => (
							<tr key={item.item_id} className="border-b border-gray-50 hover:bg-gray-50">
								<td className="py-3 font-medium">{item.item_name}</td>
								<td className="py-3">{item.category}</td>
								<td className="py-3">{formatPrice(item.price)}</td>
								<td className="py-3">{item.prep_time_estimate} min</td>
								<td className="py-3">
									<Badge
										text={item.is_available ? 'Available' : 'Unavailable'}
										variant={item.is_available ? 'success' : 'danger'}
									/>
								</td>
								<td className="py-3 whitespace-nowrap">
									<button
										onClick={() => openEditModal(item)}
										className="text-blue-600 hover:text-blue-800 text-sm font-medium mr-3"
									>
										Edit
									</button>
									<button
										onClick={() => handleDelete(item.item_id, item.item_name)}
										className="text-red-500 hover:text-red-700 text-sm font-medium"
									>
										Delete
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>

			{/* Add Modal */}
			<Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add Menu Item">
				<div className="space-y-4">
					<div>
						<label className="input-label">Name</label>
						<input className="input-field" value={formData.item_name} onChange={e => setFormData({...formData, item_name: e.target.value})} />
					</div>
					<div>
						<label className="input-label">Category</label>
						<select className="input-field" value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})}>
							<option>Beverages</option><option>Snacks</option><option>Sandwiches</option><option>Main Course</option><option>Desserts</option>
						</select>
					</div>
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">Price</label>
							<input type="number" className="input-field" value={formData.price} onChange={e => setFormData({...formData, price: e.target.value})} />
						</div>
						<div>
							<label className="input-label">Prep Time (min)</label>
							<input type="number" className="input-field" value={formData.prep_time_estimate} onChange={e => setFormData({...formData, prep_time_estimate: e.target.value})} />
						</div>
					</div>
					<div>
						<label className="input-label">Complexity Score</label>
						<select className="input-field" value={formData.complexity_score} onChange={e => setFormData({...formData, complexity_score: e.target.value})}>
							<option value={1}>1</option>
							<option value={2}>2</option>
							<option value={3}>3</option>
						</select>
					</div>
					<div>
						<label className="input-label">Availability</label>
						<select className="input-field" value={formData.is_available ? 'true' : 'false'} onChange={e => setFormData({...formData, is_available: e.target.value === 'true'})}>
							<option value="true">Available</option>
							<option value="false">Unavailable</option>
						</select>
					</div>
					{!formData.is_available && (
						<div>
							<label className="input-label">Unavailable Reason</label>
							<input className="input-field" value={formData.unavailable_reason} onChange={e => setFormData({...formData, unavailable_reason: e.target.value})} />
						</div>
					)}
					<div>
						<label className="input-label">Item Picture</label>
						<input
							type="file"
							accept="image/*"
							className="input-field"
							onChange={e => setSelectedImage(e.target.files?.[0] || null)}
						/>
					</div>
					<button onClick={handleAdd} disabled={adding} className="btn-primary w-full">{adding ? 'Adding...' : 'Add Item'}</button>
				</div>
			</Modal>

			{/* Edit Modal */}
			<Modal isOpen={showEditModal} onClose={() => setShowEditModal(false)} title="Edit Menu Item">
				<div className="space-y-4">
					<div>
						<label className="input-label">Name</label>
						<input className="input-field" value={editFormData.item_name} onChange={e => setEditFormData({...editFormData, item_name: e.target.value})} />
					</div>
					<div>
						<label className="input-label">Category</label>
						<select className="input-field" value={editFormData.category} onChange={e => setEditFormData({...editFormData, category: e.target.value})}>
							<option>Beverages</option><option>Snacks</option><option>Sandwiches</option><option>Main Course</option><option>Desserts</option>
						</select>
					</div>
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">Price</label>
							<input type="number" className="input-field" value={editFormData.price} onChange={e => setEditFormData({...editFormData, price: e.target.value})} />
						</div>
						<div>
							<label className="input-label">Prep Time (min)</label>
							<input type="number" className="input-field" value={editFormData.prep_time_estimate} onChange={e => setEditFormData({...editFormData, prep_time_estimate: e.target.value})} />
						</div>
					</div>
					<div>
						<label className="input-label">Complexity Score</label>
						<select className="input-field" value={editFormData.complexity_score} onChange={e => setEditFormData({...editFormData, complexity_score: e.target.value})}>
							<option value={1}>1</option>
							<option value={2}>2</option>
							<option value={3}>3</option>
						</select>
					</div>
					<div>
						<label className="input-label">Availability</label>
						<select className="input-field" value={editFormData.is_available ? 'true' : 'false'} onChange={e => setEditFormData({...editFormData, is_available: e.target.value === 'true'})}>
							<option value="true">Available</option>
							<option value="false">Unavailable</option>
						</select>
					</div>
					{!editFormData.is_available && (
						<div>
							<label className="input-label">Unavailable Reason</label>
							<input className="input-field" value={editFormData.unavailable_reason} onChange={e => setEditFormData({...editFormData, unavailable_reason: e.target.value})} />
						</div>
					)}
					<div>
						<label className="input-label">Change Picture</label>
						<input
							type="file"
							accept="image/*"
							className="input-field"
							onChange={e => setSelectedEditImage(e.target.files?.[0] || null)}
						/>
					</div>
					<button onClick={handleEdit} disabled={editing} className="btn-primary w-full">{editing ? 'Saving...' : 'Save Changes'}</button>
				</div>
			</Modal>
		</div>
	)
}
